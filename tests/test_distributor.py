#!/usr/bin/env python
from brownie import Contract, chain, ZERO_ADDRESS
from brownie import DfxDistributor, DfxUpgradeableProxy
from datetime import datetime
import pytest

from utils.chain import fastforward_chain, fastforward_chain_weeks
from utils.gauges import deposit_lp_tokens, setup_distributor
from utils.helper import fund_multisigs
from utils.gauges import setup_distributor, setup_gauge_controller
from .constants import EMISSION_RATE, TOTAL_DFX_REWARDS


# Deploy distributor without affecting chain time
@pytest.fixture(scope="function")
def _distributor(DFX, gauge_controller, deploy_account, multisig_0, multisig_1):
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
    distributor,
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
        distributor,
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


# ## Helpers
# def chain_time(out=False):
#     now = int(chain.time())
#     if out:
#         print("Chain time:", datetime.fromtimestamp(now))
#     return now


# ## Tests
# # Set deploy time to: Oct 17, 2023 12:00:00 UTC
# # Deploy contract, epoch start is: Oct 12, 2023 00:00:00 UTC
# def test_epoch_start(_distributor):
#     # Set chain time to a Tuesday
#     t0 = int(datetime(2023, 10, 17, 12, 0, 0).timestamp())
#     fastforward_chain(t0)
#     assert chain_time() == t0, "Chain time not Oct 17, 2023 at 12:00:00"

#     start_epoch = _distributor.startEpochTime()
#     assert start_epoch == 1697068800, "Epoch start not Oct 12, 2023, at 00:00:00"


# def test_early_distribution(_distributor, _gauge, lpt_L1, deploy_account):
#     # check that we have been pre-minted LP tokens
#     assert (
#         lpt_L1.balanceOf(deploy_account) == 1_000_000_000 * 1e18
#     ), "Insufficient LPT balance"


def test_start_distribution():
    pass
