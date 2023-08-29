#!/usr/bin/env python
from brownie import chain, ZERO_ADDRESS
from datetime import datetime

from utils.chain import (
    fastforward_chain,
    fastforward_chain_weeks,
    # fastforward_chain_anvil as fastforward_chain,
    # fastforward_chain_weeks_anvil as fastforward_chain_weeks,
)
from utils.gas import gas_strategy


def add_gauge_reward(DFX_OFT, streamer, gauge, mock_ccip_router, multisig_0):
    # update authorized user for childchainstreamer rewards
    # DEV: This will be the address of the CCTP contract which is calling "notify_reward_amount"
    # on ChildChainStreamer
    streamer.set_reward_distributor(
        DFX_OFT, mock_ccip_router, {"from": multisig_0, "gas_price": gas_strategy}
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


def advance_epoch(DFX_OFT, streamer, gauge, router, deploy_account, multisig_0):
    fastforward_chain_weeks(num_weeks=1, delta=10)
    router.transfer(
        DFX_OFT, streamer, 1e23, {"from": multisig_0, "gas_price": gas_strategy}
    )
    streamer.notify_reward_amount(
        DFX_OFT, {"from": multisig_0, "gas_price": gas_strategy}
    )

    tx = gauge.claimable_reward_write(
        deploy_account, DFX_OFT, {"from": deploy_account, "gas_price": gas_strategy}
    )
    available_rewards = tx.return_value

    gauge.claim_rewards({"from": deploy_account, "gas_price": gas_strategy})
    # rewards = gauge.claimable_reward(deploy_account, DFX_OFT)
    claimed_rewards = gauge.claimed_reward(deploy_account, DFX_OFT)

    now = datetime.fromtimestamp(chain.time())
    print(f"-- {now}")
    print(f"Streamer balance: {DFX_OFT.balanceOf(streamer)/1e18}")
    print(f"Gauge balance: {DFX_OFT.balanceOf(gauge)/1e18}")
    print(f"User staked LPT: {gauge.balanceOf(deploy_account)/1e18}")
    # print(available_rewards)
    # print(f"User available rewards: {available_rewards/1e18}")
    # print(f"User claimed rewards: {claimed_rewards/1e18}")
    # print(f"User balance: {DFX_OFT.balanceOf(deploy_account)/1e18}")
