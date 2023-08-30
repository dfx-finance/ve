#!/usr/bin/env python
from brownie import chain, ZERO_ADDRESS
from datetime import datetime

from utils.chain import (
    fastforward_chain,
    fastforward_chain_weeks,
    # fastforward_chain_anvil as fastforward_chain,
    # fastforward_chain_weeks_anvil as fastforward_chain_weeks,
)


def set_gauge_reward(DFX_OFT, streamer, gauge, router, multisig_0):
    # update authorized user for childchainstreamer rewards
    # DEV: This will be the address of the CCTP contract which is calling "notify_reward_amount"
    # on ChildChainStreamer
    streamer.set_reward_distributor(DFX_OFT, router, {"from": multisig_0})

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
        {"from": multisig_0},
    )


def advance_epoch(
    DFX_OFT, streamer, gauge, router, deploy_account, multisig_0, multisig_1
):
    fastforward_chain_weeks(num_weeks=1, delta=10)
    router.transferToken(DFX_OFT, streamer, 1e23, {"from": multisig_0})
    streamer.notify_reward_amount(DFX_OFT, {"from": multisig_0})

    # tx = gauge.claimable_reward_write(deploy_account, DFX_OFT, {"from": deploy_account})
    # print(tx.value)
    # available_rewards = 0

    available_rewards = gauge.claimable_reward(deploy_account, DFX_OFT)
    gauge.claim_rewards({"from": deploy_account})
    claimed_rewards = gauge.claimed_reward(deploy_account, DFX_OFT)

    now = datetime.fromtimestamp(chain.time())
    print(f"-- {now}")
    print(f"Streamer balance: {DFX_OFT.balanceOf(streamer)/1e18}")
    print(f"Gauge balance: {DFX_OFT.balanceOf(gauge)/1e18}")
    print(f"User staked LPT: {gauge.balanceOf(deploy_account)/1e18}")
    print(f"User available rewards: {available_rewards/1e18}")
    print(f"User claimed rewards: {claimed_rewards/1e18}")
    print(f"User balance: {DFX_OFT.balanceOf(deploy_account)/1e18}")
