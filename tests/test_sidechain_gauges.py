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
    RootGaugeCctp,
    DfxUpgradeableProxy,
    DFX,
    gauge_controller,
    distributor,
    three_gauges,
    deploy_account,
    multisig_0,
    multisig_1,
):
    ##
    ## epoch 0: do nothing
    ##
    print(f"Epoch {distributor.miningEpoch()}: {DFX.balanceOf(distributor) / 1e18} DFX")

    ##
    ## epoch 1: distributer rewards to gauges
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
    ## epoch 2: deploy L2 gauge, add to gauge controller and distribute rewards
    ##
    fastforward_chain_weeks(num_weeks=0, delta=0, log=True)

    l2_gauge = deploy_l2_gauge(
        RootGaugeCctp,
        DfxUpgradeableProxy,
        DFX,
        gauge_controller,
        distributor,
        deploy_account,
        multisig_0,
        multisig_1,
    )

    add_to_gauge_controller(
        gauge_controller, l2_gauge, multisig_0, add_placeholder=True
    )

    # set l2 gauge as a delegate for automating distribution
    distributor.setDelegateGauge(
        l2_gauge,
        l2_gauge,
        True,
        {"from": multisig_0, "gas_price": gas_strategy},
    )
    print(f"Rewards delegate is set: {distributor.isInterfaceKnown(l2_gauge)}")

    distributor.distributeRewardToMultipleGauges(
        [*three_gauges, l2_gauge],
        {"from": multisig_0, "gas_price": gas_strategy},
    )
    print(f"Epoch {distributor.miningEpoch()}: {DFX.balanceOf(distributor) / 1e18} DFX")
    for gauge in [*three_gauges, l2_gauge]:
        print(f"{gauge.symbol()}: {DFX.balanceOf(gauge) / 1e18}")

    ##
    ## epoch 3: distribute rewards, do nothing
    ##
    fastforward_chain_weeks(num_weeks=0, delta=0, log=True)
    distributor.distributeRewardToMultipleGauges(
        [*three_gauges, l2_gauge],
        {"from": multisig_0, "gas_price": gas_strategy},
    )
    print(f"Epoch {distributor.miningEpoch()}: {DFX.balanceOf(distributor) / 1e18} DFX")
    for gauge in [*three_gauges, l2_gauge]:
        print(f"{gauge.symbol()}: {DFX.balanceOf(gauge) / 1e18}")


##
## Utils
##
def deploy_l2_gauge(
    RootGaugeCctp,
    DfxUpgradeableProxy,
    dfx,
    gauge_controller,
    distributor,
    deploy_account,
    multisig_0,
    multisig_1,
):
    # deploy gauge logic
    gauge_implementation = RootGaugeCctp.deploy(
        {"from": deploy_account, "gas_price": gas_strategy},
    )

    # deploy gauge proxy and initialize
    gauge_initializer_calldata = gauge_implementation.initialize.encode_input(
        "l2-gauge",
        dfx,
        gauge_controller,
        distributor,
        42161,
        "0x0000000000000000000000000000000000000001",
        multisig_0,
    )
    proxy = DfxUpgradeableProxy.deploy(
        gauge_implementation.address,
        multisig_1,
        gauge_initializer_calldata,
        {"from": deploy_account, "gas_price": gas_strategy},
    )

    # load gauge interface on proxy for non-admin users
    gauge_proxy = Contract.from_abi("RootGaugeCctp", proxy, RootGaugeCctp.abi)
    return gauge_proxy


def add_to_gauge_controller(gauge_controller, gauge, multisig_0, add_placeholder=False):
    if add_placeholder:
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
        gauge,
        2,
        DEFAULT_GAUGE_WEIGHT,
        {"from": multisig_0, "gas_price": gas_strategy},
    )
