#!/usr/bin/env python
from brownie import Contract, chain, reverts, ZERO_ADDRESS
from brownie import DfxDistributor, DfxUpgradeableProxy
from datetime import datetime
import pytest

from utils.chain import fastforward_chain, fastforward_chain_weeks
from utils.gauges import deposit_lp_tokens, setup_distributor
from utils.helper import fund_multisigs
from utils.gauges import setup_distributor, setup_gauge_controller
from .constants import EMISSION_RATE, WEEK


def set_chain_time():
    # Set chain time to a Tuesday
    t0 = int(datetime(2025, 4, 15, 12, 0, 0).timestamp())
    fastforward_chain(t0)
    return t0


# Deploy distributor without affecting chain time
@pytest.fixture(scope="function")
def _distributor(DFX, gauge_controller, deploy_account, multisig_0, multisig_1):
    set_chain_time()

    # Deploy DfxDistributor logic
    dfx_distributor = DfxDistributor.deploy({"from": deploy_account})

    # Deploy DfxDistributor proxy
    distributor_initializer_calldata = dfx_distributor.initialize.encode_input(
        DFX,
        gauge_controller,
        0,
        0,
        # should consider using another multisig to deal with access control
        multisig_0,
        multisig_0,
        ZERO_ADDRESS,
    )
    proxy = DfxUpgradeableProxy.deploy(
        dfx_distributor.address,
        multisig_1,
        distributor_initializer_calldata,
        {"from": deploy_account},
    )

    # Load Distributor ABI on proxy address
    dfx_distributor_proxy = Contract.from_abi(
        "DfxDistributor", proxy.address, DfxDistributor.abi
    )

    return dfx_distributor_proxy


# Deploys a LiquidityGaugeV4 contract as found on Layer 1
@pytest.fixture(scope="function")
def _gauge(
    DFX,
    veDFX,
    LiquidityGaugeV4,
    DfxUpgradeableProxy,
    veboost_proxy,
    _distributor,
    lpt_L1,
    deploy_account,
    multisig_0,
    multisig_1,
):
    # deploy gauge logic
    gauge = LiquidityGaugeV4.deploy({"from": deploy_account})

    # deploy gauge behind proxy
    gauge_initializer_calldata = gauge.initialize.encode_input(
        lpt_L1,
        multisig_0,
        DFX,
        veDFX,
        veboost_proxy,
        _distributor,
    )
    dfx_upgradeable_proxy = DfxUpgradeableProxy.deploy(
        gauge.address,
        multisig_1,
        gauge_initializer_calldata,
        {"from": deploy_account},
    )

    gauge_proxy = Contract.from_abi(
        "LiquidityGaugeV4", dfx_upgradeable_proxy, LiquidityGaugeV4.abi
    )
    return gauge_proxy


# handle setup logic required for each unit test
@pytest.fixture(scope="function", autouse=True)
def setup(
    DFX, gauge_controller, _gauge, _distributor, multisig_0, multisig_1, deploy_account
):
    fund_multisigs(deploy_account, [multisig_0])

    # setup gauges and distributor
    setup_gauge_controller(gauge_controller, [_gauge], multisig_0)

    # Params:
    # - reward token
    # - distributor contract
    # - account from which to mint and provide rewards to distributor contract
    # - account which administers the distributor contract
    # - rate dependent on tokens available and weekly reduction (see spreadsheet)
    setup_distributor(
        DFX, _distributor, deploy_account, multisig_0, EMISSION_RATE, 1_000_000 * 1e18
    )


## Helpers
def chain_time(out=False):
    now = int(chain.time())
    if out:
        print("Chain time:", datetime.fromtimestamp(now))
    return now


## Tests
# Set deploy time to: Apr 15, 2025 12:00:00 UTC
# Deploy contract, epoch start is: Apr 10, 2025 00:00:00 UTC
def test_epoch_start(_distributor):
    # Set chain time to a Tuesday
    t0 = set_chain_time()
    fastforward_chain(t0)

    assert t0 - 5 <= chain_time() <= t0 + 5, "Chain time not Apr 15, 2025 at 12:00:00"

    start_epoch = _distributor.startEpochTime()
    assert (
        1744243195 <= start_epoch <= 1744243205
    ), "Epoch start not Apr 10, 2023 at 00:00:00"


def test_early_distribution(
    DFX, _distributor, _gauge, lpt_L1, deploy_account, multisig_0
):
    assert _distributor.miningEpoch() == 0, "Unexpected epoch"

    # check that we have been pre-minted LP tokens
    assert (
        lpt_L1.balanceOf(deploy_account) == 1_000_000_000 * 1e18
    ), "Insufficient LPT balance"

    # deposit tokens to gauge
    deposit_lp_tokens(lpt_L1, _gauge, deploy_account)

    fastforward_chain(chain_time() + 10)
    _distributor.distributeReward(_gauge, {"from": multisig_0})
    assert _distributor.miningEpoch() == 0, "Unexpected epoch"

    assert DFX.balanceOf(_gauge) == 0, "Gauge received rewards before first epoch"


def test_start_distribution(
    DFX, gauge_controller, _distributor, _gauge, lpt_L1, multisig_0, deploy_account
):
    assert _distributor.miningEpoch() == 0, "Unexpected epoch"

    # deposit tokens to gauge
    deposit_lp_tokens(lpt_L1, _gauge, deploy_account)

    # fast-forward to start of epoch 1
    fastforward_chain_weeks(num_weeks=0)
    gauge_controller.gauge_relative_weight_write(_gauge, {"from": multisig_0})
    weight = gauge_controller.gauge_relative_weight(_gauge)
    assert weight == 1e18, "Unexpected gauge weight"
    _distributor.distributeReward(_gauge, {"from": multisig_0})
    assert (
        DFX.balanceOf(_gauge) == 120020493396596944838400
    ), "Unexpected amount of rewards"
    assert _distributor.miningEpoch() == 1, "Unexpected epoch"

    # fast-forward to start of epoch 2
    fastforward_chain_weeks(num_weeks=0)
    gauge_controller.gauge_relative_weight_write(_gauge, {"from": multisig_0})
    weight = gauge_controller.gauge_relative_weight(_gauge)
    assert weight == 1e18, "Unexpected gauge weight"
    _distributor.distributeReward(_gauge, {"from": multisig_0})
    assert (
        DFX.balanceOf(_gauge) == 239108777417451531744000
    ), "Unexpected amount of rewards"
    assert _distributor.miningEpoch() == 2, "Unexpected epoch"


# Can update mining parameters at start of epoch. Reverts if called too soon.
def test_update_mining_parameters(_distributor, multisig_0):
    with reverts():
        _distributor.updateMiningParameters({"from": multisig_0})

    fastforward_chain_weeks(num_weeks=0)
    _distributor.updateMiningParameters({"from": multisig_0})

    fastforward_chain(chain_time() + 10)
    with reverts():
        _distributor.updateMiningParameters({"from": multisig_0})

    fastforward_chain_weeks(num_weeks=0)
    _distributor.updateMiningParameters({"from": multisig_0})
