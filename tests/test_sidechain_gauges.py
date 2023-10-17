#!/usr/bin/env python
from brownie import chain
import pytest

from utils.chain import (
    fastforward_chain,
    fastforward_chain_weeks,
    # fastforward_chain_anvil as fastforward_chain,
    # fastforward_chain_weeks_anvil as fastforward_chain_weeks,
)
from utils.gauges import setup_distributor, setup_gauge_controller
from utils.helper import fund_multisigs
from .constants import EMISSION_RATE, TOTAL_DFX_REWARDS
from .helpers_sidechain_gauges import add_to_gauge_controller


# handle setup logic required for each unit test
@pytest.fixture(scope="function", autouse=True)
def setup(
    DFX,
    gauge_controller,
    three_gauges_L1,
    distributor,
    deploy_account,
    multisig_0,
):
    fund_multisigs(deploy_account, [multisig_0])

    # setup gauges and distributor
    setup_gauge_controller(gauge_controller, three_gauges_L1, multisig_0)

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


def test_l2_gauge_timetravel(
    DFX,
    gauge_controller,
    distributor,
    three_gauges_L1,
    root_gauge_L1,
    multisig_0,
):
    # provide root gauge with gas money
    multisig_0.transfer(root_gauge_L1.address, 5e17)

    ##
    ## epoch 0: do nothing
    ##
    print(f"Epoch {distributor.miningEpoch()}: {DFX.balanceOf(distributor) / 1e18} DFX")

    ##
    ## epoch 1: distributer rewards to gauges
    ##
    fastforward_chain_weeks(num_weeks=0, delta=0, log=True)
    distributor.distributeRewardToMultipleGauges(
        three_gauges_L1,
        {"from": multisig_0},
    )
    print(f"Epoch {distributor.miningEpoch()}: {DFX.balanceOf(distributor) / 1e18} DFX")
    for gauge in three_gauges_L1:
        print(f"{gauge.symbol()}: {DFX.balanceOf(gauge) / 1e18}")

    ##
    ## epoch 2: deploy L2 gauge, add to gauge controller and distribute rewards
    ##
    fastforward_chain_weeks(num_weeks=0, delta=0, log=True)

    add_to_gauge_controller(
        gauge_controller, root_gauge_L1, multisig_0, add_placeholder=True
    )

    # set l2 gauge as a delegate for automating distribution by calling RootGauge notifyReward function
    distributor.setDelegateGauge(
        root_gauge_L1,
        root_gauge_L1,
        True,
        {"from": multisig_0},
    )
    print(f"Rewards delegate is set: {distributor.isInterfaceKnown(root_gauge_L1)}")

    distributor.distributeRewardToMultipleGauges(
        [*three_gauges_L1, root_gauge_L1],
        {"from": multisig_0},
    )

    print(f"Epoch {distributor.miningEpoch()}: {DFX.balanceOf(distributor) / 1e18} DFX")
    for gauge in [*three_gauges_L1, root_gauge_L1]:
        print(f"{gauge.symbol()}: {DFX.balanceOf(gauge) / 1e18}")

    ##
    ## epoch 3: distribute rewards, do nothing
    ##
    fastforward_chain_weeks(num_weeks=0, delta=0, log=True)
    distributor.distributeRewardToMultipleGauges(
        [*three_gauges_L1, root_gauge_L1],
        {"from": multisig_0},
    )
    print(f"Epoch {distributor.miningEpoch()}: {DFX.balanceOf(distributor) / 1e18} DFX")
    for gauge in [*three_gauges_L1, root_gauge_L1]:
        print(f"{gauge.symbol()}: {DFX.balanceOf(gauge) / 1e18}")


def test_cctp_root_gauge_send(DFX, root_gauge_L1, deploy_account, multisig_0):
    root_gauge_L1.setDistributor(deploy_account, {"from": multisig_0})

    # provide gauge with gas money
    multisig_0.transfer(root_gauge_L1.address, 5e17)

    reward_amount = 1e23
    DFX.mint(
        deploy_account,
        reward_amount,
        {"from": deploy_account},
    )
    DFX.transfer(
        root_gauge_L1,
        reward_amount,
        {"from": deploy_account},
    )
    root_gauge_L1.notifyReward(
        root_gauge_L1.address,
        reward_amount,
        {"from": deploy_account},
    )
