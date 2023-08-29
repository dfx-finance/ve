#!/usr/bin/env python
import pytest

from utils.gas import gas_strategy
from utils.helper import fund_multisigs
from .helpers_childchainstreamer import add_gauge_reward, advance_epoch


# handle setup logic required for each unit test
@pytest.fixture(scope="function", autouse=True)
def setup(deploy_account, multisig_0):
    fund_multisigs(deploy_account, [multisig_0])


def test_receive_rewards_ccip(DFX_OFT, child_chain_streamer, deploy_account):
    DFX_OFT.transfer(
        child_chain_streamer,
        1e18,
        {"from": deploy_account, "gas_price": gas_strategy},
    )
    child_chain_streamer.notify_reward_amount(DFX_OFT)


def test_stream_to_gauge(
    DFX_OFT,
    lpt_L2,
    child_chain_streamer,
    child_gauge_L2,
    mock_ccip_router,
    deploy_account,
    multisig_0,
):
    add_gauge_reward(
        DFX_OFT,
        child_chain_streamer,
        child_gauge_L2,
        mock_ccip_router,
        multisig_0,
    )

    # give distributor rewards
    mock_ccip_router.transfer(
        DFX_OFT,
        child_chain_streamer,
        1e23,
        {"from": multisig_0, "gas_price": gas_strategy},
    )
    child_chain_streamer.notify_reward_amount(
        DFX_OFT, {"from": multisig_0, "gas_price": gas_strategy}
    )

    # deposit lpt to l2 gauge
    max_uint256 = 2**256 - 1
    lpt_L2.approve(
        child_gauge_L2, max_uint256, {"from": deploy_account, "gas_price": gas_strategy}
    )
    child_gauge_L2.deposit(1e18, {"from": deploy_account, "gas_price": gas_strategy})

    print(child_gauge_L2.balanceOf(deploy_account))

    print(f"DFX_OFT addr: {DFX_OFT}")
    print(f"Gauge reward token addr: {child_gauge_L2.reward_tokens(0)}")
    for _ in range(4):
        advance_epoch(
            DFX_OFT,
            child_chain_streamer,
            child_gauge_L2,
            mock_ccip_router,
            deploy_account,
            multisig_0,
        )
