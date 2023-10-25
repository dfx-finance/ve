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


def advance_epoch(DFX_OFT, streamer, router, multisig_0):
    fastforward_chain_weeks(num_weeks=1, delta=10)
    router.transferToken(DFX_OFT, streamer, 1e23, {"from": multisig_0})
    streamer.notify_reward_amount(DFX_OFT, {"from": multisig_0})


def log_ve_gauge(DFX_OFT, streamer, gauge):
    print(f"Streamer balance: {DFX_OFT.balanceOf(streamer)/1e18}")
    print(f"Gauge balance: {DFX_OFT.balanceOf(gauge)/1e18}")


def log_ve_user(DFX_OFT, gauge, user_account, label=None, claim=False):
    # tx = gauge.claimable_reward_write(deploy_account, DFX_OFT, {"from": deploy_account})
    # print(tx.value)
    # available_rewards = 0
    available_rewards = gauge.claimable_reward(user_account, DFX_OFT)
    if claim:
        gauge.claim_rewards({"from": user_account})
    claimed_rewards = gauge.claimed_reward(user_account, DFX_OFT)

    user_label = f"User {label}" if label else "User"
    print(f"{user_label} staked LPT: {gauge.balanceOf(user_account)/1e18}")
    print(f"{user_label} available rewards: {available_rewards/1e18}")
    print(f"{user_label} claimed rewards: {claimed_rewards/1e18}")
    print(f"{user_label} DFX balance: {DFX_OFT.balanceOf(user_account)/1e18}")
