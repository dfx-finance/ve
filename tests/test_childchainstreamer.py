#!/usr/bin/env python
from brownie import chain
from datetime import datetime
import math
import pytest

from utils.helper import fund_multisigs
from .helpers_childchainstreamer import advance_epoch, set_gauge_reward


# handle setup logic required for each unit test
@pytest.fixture(scope="function", autouse=True)
def setup(deploy_account, multisig_0):
    fund_multisigs(deploy_account, [multisig_0])


def test_receive_rewards_ccip(
    DFX_OFT, child_chain_streamer, mock_ccip_router, deploy_account, multisig_0
):
    # update authorized user for childchainstreamer rewards
    # DEV: This will be the address of the CCTP contract which is calling "notify_reward_amount"
    # on ChildChainStreamer
    child_chain_streamer.set_reward_distributor(
        DFX_OFT, mock_ccip_router, {"from": multisig_0}
    )

    DFX_OFT.transfer(
        child_chain_streamer,
        1e23,
        {"from": deploy_account},
    )

    # message id, source chain selector, sender, data, destTokenAmounts
    msg = [0, 0, 0, 0, [[DFX_OFT, 1e23]]]
    child_chain_streamer.ccipReceive(msg, {"from": mock_ccip_router})

    # check that token distribution/second will equal the total rewards
    # provided for the epoch
    rate = child_chain_streamer.reward_data(DFX_OFT)[2]
    assert math.isclose(rate * 60 * 60 * 24 * 7, 1e23, rel_tol=1e-4)


def test_stream_to_gauge(
    DFX_OFT,
    lpt_L2,
    child_chain_streamer,
    child_gauge_L2,
    mock_ccip_router,
    deploy_account,
    multisig_0,
    multisig_1,
):
    print(f"--- Start time: {datetime.fromtimestamp(chain.time())}")

    set_gauge_reward(
        DFX_OFT,
        child_chain_streamer,
        child_gauge_L2,
        mock_ccip_router,
        multisig_0,
    )

    # give distributor rewards
    mock_ccip_router.transferToken(
        DFX_OFT,
        child_chain_streamer,
        1e23,
        {"from": multisig_0},
    )
    child_chain_streamer.notify_reward_amount(DFX_OFT, {"from": mock_ccip_router})

    # print(mock_ccip_router, child_chain_streamer.reward_data(DFX_OFT))

    # deposit lpt to l2 gauge
    max_uint256 = 2**256 - 1
    lpt_L2.approve(child_gauge_L2, max_uint256, {"from": deploy_account})
    child_gauge_L2.deposit(1e18, {"from": deploy_account})

    print(f"User gauge balance: {child_gauge_L2.balanceOf(deploy_account)/1e18} LPT")
    print(
        f"Gauge reward is DFX_OFT: {DFX_OFT == child_gauge_L2.reward_tokens(0)} ({DFX_OFT})"
    )

    for _ in range(3):
        advance_epoch(
            DFX_OFT,
            child_chain_streamer,
            child_gauge_L2,
            mock_ccip_router,
            deploy_account,
            multisig_0,
            multisig_1,
        )
