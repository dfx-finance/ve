#!/usr/bin/env python
from brownie import ZERO_ADDRESS
import pytest

from utils.gas import gas_strategy
from utils.helper import fund_multisigs
from .helpers_childchainstreamer import advance_epoch


# handle setup logic required for each unit test
@pytest.fixture(scope="function", autouse=True)
def setup(deploy_account, multisig_0):
    fund_multisigs(deploy_account, [multisig_0])


def deploy_l2_contracts(
    ERC20LP,
    RewardsOnlyGauge,
    ChildChainStreamer,
    DFX_OFT,
    deploy_account,
    multisig_0,
    multisig_1,
):
    # L2 LPT for depositing into gauge
    lpt = ERC20LP.deploy(
        "L2 Test Gauge",
        "L2TG",
        18,
        1e18,
        {"from": deploy_account, "gas_price": gas_strategy},
    )

    # deploy L2 read-only gauge
    # DEV: this gauge will distribute rewards pro-rata to staked LPTs by their share
    # in the gauge at the time rewards are received
    gauge = RewardsOnlyGauge.deploy(
        multisig_0, lpt, {"from": deploy_account, "gas_price": gas_strategy}
    )

    # deploy L2 reward distributor
    # DEV: This is a 1-to-1 relationship with a RewardsOnlyGauge
    streamer = ChildChainStreamer.deploy(
        deploy_account,
        gauge,
        DFX_OFT,
        {"from": deploy_account, "gas_price": gas_strategy},
    )

    # update authorized user for childchainstreamer rewards
    # DEV: This will be the address of the CCTP contract which is calling "notify_reward_amount"
    # on ChildChainStreamer
    streamer.set_reward_distributor(
        DFX_OFT, multisig_1, {"from": deploy_account, "gas_price": gas_strategy}
    )

    # set rewards contract on gauge
    # DEV: cannot be set while gauge has 0 deposits?
    gauge.set_rewards(
        streamer,
        streamer.signatures["get_reward"],
        [
            DFX_OFT,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
        ],
        {"from": multisig_0, "gas_price": gas_strategy},
    )
    return lpt, streamer, gauge


def test_stream_to_gauge(
    DFX_OFT,
    ERC20LP,
    ChildChainStreamer,
    RewardsOnlyGauge,
    deploy_account,
    multisig_0,
    multisig_1,
):
    lpt, streamer, gauge = deploy_l2_contracts(
        ERC20LP,
        RewardsOnlyGauge,
        ChildChainStreamer,
        DFX_OFT,
        deploy_account,
        multisig_0,
        multisig_1,
    )

    # distribute rewards
    DFX_OFT.transfer(
        streamer, 1e23, {"from": deploy_account, "gas_price": gas_strategy}
    )
    streamer.notify_reward_amount(
        DFX_OFT, {"from": multisig_1, "gas_price": gas_strategy}
    )

    # deposit lpt to l2 gauge
    max_uint256 = 2**256 - 1
    lpt.approve(gauge, max_uint256, {"from": deploy_account, "gas_price": gas_strategy})
    gauge.deposit(1e18, {"from": deploy_account, "gas_price": gas_strategy})

    print(f"DFX_OFT addr: {DFX_OFT}")
    print(f"Gauge reward token addr: {gauge.reward_tokens(0)}")
    advance_epoch(DFX_OFT, streamer, gauge, deploy_account, multisig_1)
    advance_epoch(DFX_OFT, streamer, gauge, deploy_account, multisig_1)
    advance_epoch(DFX_OFT, streamer, gauge, deploy_account, multisig_1)
    advance_epoch(DFX_OFT, streamer, gauge, deploy_account, multisig_1)
