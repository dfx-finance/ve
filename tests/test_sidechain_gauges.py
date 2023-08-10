#!/usr/bin/env python
from brownie import chain, Contract, ZERO_ADDRESS
import pytest

from utils.chain import (
    fastforward_chain,
    fastforward_chain_weeks,
    # fastforward_chain_anvil as fastforward_chain,
    # fastforward_chain_weeks_anvil as fastforward_chain_weeks,
)
from utils.constants import (
    # DEFAULT_TYPE_WEIGHT,
    # DEFAULT_GAUGE_TYPE,
    DEFAULT_GAUGE_WEIGHT,
)
from utils.gauges import setup_distributor, setup_gauge_controller
from utils.gas import gas_strategy
from utils.helper import fund_multisigs
from .constants import EMISSION_RATE, TOTAL_DFX_REWARDS


# handle setup logic required for each unit test
@pytest.fixture(scope="function", autouse=True)
def setup(
    DFX,
    gauge_controller,
    three_gauges,
    distributor,
    deploy_account,
    multisig_0,
):
    fund_multisigs(deploy_account, [multisig_0])

    # setup gauges and distributor
    setup_gauge_controller(gauge_controller, three_gauges, multisig_0)

    # Params:
    # - reward token
    # - distributor contract
    # - account from which to mint and provide rewards to distributor contract
    # - account which administers the distributor contract
    # - rate dependent on tokens available and weekly reduction (see spreadsheet)
    setup_distributor(
        DFX,
        distributor,
        deploy_account,
        multisig_0,
        EMISSION_RATE,
        TOTAL_DFX_REWARDS,
    )


@pytest.fixture(scope="function", autouse=True)
def teardown():
    yield
    chain.reset()


def test_l2_gauges(
    ERC20LP,
    LiquidityGaugeV4,
    RootGaugeDelegateOft,
    DfxUpgradeableProxy,
    DFX,
    veDFX,
    gauge_controller,
    distributor,
    veboost_proxy,
    three_gauges,
    deploy_account,
    multisig_0,
    multisig_1,
):
    ##
    ## epoch 0
    ##
    print(f"Epoch {distributor.miningEpoch()}: {DFX.balanceOf(distributor) / 1e18} DFX")

    ##
    ## epoch 1
    ##
    fastforward_chain_weeks(num_weeks=0, delta=0, log=True)
    distributor.distributeRewardToMultipleGauges(
        three_gauges,
        {"from": multisig_0, "gas_price": gas_strategy},
    )
    print(f"Epoch {distributor.miningEpoch()}: {DFX.balanceOf(distributor) / 1e18} DFX")
    for gauge in three_gauges:
        print(f"{gauge.symbol()}: {DFX.balanceOf(gauge) / 1e18}")

    ##
    ## epoch 2
    ##
    fastforward_chain_weeks(num_weeks=0, delta=0, log=True)

    # deploy lpt for test gauge
    # dev: this won't exist for RootGaugeOft
    name, symbol = ("L2 LP Token", "L2Pair")
    lpt = ERC20LP.deploy(
        name, symbol, 18, 1e9, {"from": deploy_account, "gas_price": gas_strategy}
    )
    assert lpt.symbol() == "L2Pair"

    # deploy gauge logic
    gauge = LiquidityGaugeV4.deploy({"from": deploy_account, "gas_price": gas_strategy})

    # deploy l2 gauge behind proxy
    gauge_initializer_calldata = gauge.initialize.encode_input(
        lpt,
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
        {"from": deploy_account, "gas_price": gas_strategy},
    )

    l2_gauge_proxy = Contract.from_abi(
        "LiquidityGaugeV4", dfx_upgradeable_proxy, LiquidityGaugeV4.abi
    )

    # add placeholder gauge type `1` to keep consistent with Angle distributor contract
    gauge_controller.add_type(
        "DFX Perpetuals",
        0,
        {"from": multisig_0, "gas_price": gas_strategy},
    )

    # add new l2 gauge type to gauge controller
    gauge_controller.add_type(
        "L2 Liquidity Pools",
        1e18,
        {"from": multisig_0, "gas_price": gas_strategy},
    )
    # add l2 gauge to gauge controller
    gauge_controller.add_gauge(
        l2_gauge_proxy,
        2,
        DEFAULT_GAUGE_WEIGHT,
        {"from": multisig_0, "gas_price": gas_strategy},
    )

    # add l2 gauge delegate
    l2_delegate = RootGaugeDelegateOft.deploy(
        DFX,
        gauge_controller,
        distributor,
        multisig_0,
        {"from": deploy_account, "gas_price": gas_strategy},
    )
    distributor.setDelegateGauge(
        ZERO_ADDRESS, l2_delegate, True, {"from": multisig_0, "gas_price": gas_strategy}
    )

    distributor.distributeRewardToMultipleGauges(
        [*three_gauges, l2_gauge_proxy],
        {"from": multisig_0, "gas_price": gas_strategy},
    )
    print(f"Epoch {distributor.miningEpoch()}: {DFX.balanceOf(distributor) / 1e18} DFX")
    for gauge in [*three_gauges, l2_gauge_proxy]:
        print(f"{gauge.symbol()}: {DFX.balanceOf(gauge) / 1e18}")
    print(f"L2 Delegate: {DFX.balanceOf(l2_delegate) / 1e18}")

    ##
    ## epoch 3
    ##
    fastforward_chain_weeks(num_weeks=0, delta=0, log=True)
    distributor.distributeRewardToMultipleGauges(
        [*three_gauges, l2_gauge_proxy],
        {"from": multisig_0, "gas_price": gas_strategy},
    )
    print(f"Epoch {distributor.miningEpoch()}: {DFX.balanceOf(distributor) / 1e18} DFX")
    for gauge in [*three_gauges, l2_gauge_proxy]:
        print(f"{gauge.symbol()}: {DFX.balanceOf(gauge) / 1e18}")
    print(f"L2 Delegate: {DFX.balanceOf(l2_delegate) / 1e18}")
