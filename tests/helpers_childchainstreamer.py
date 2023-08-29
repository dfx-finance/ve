#!/usr/bin/env python
from brownie import chain
from datetime import datetime

from utils.chain import (
    fastforward_chain,
    fastforward_chain_weeks,
    # fastforward_chain_anvil as fastforward_chain,
    # fastforward_chain_weeks_anvil as fastforward_chain_weeks,
)


from utils.gas import gas_strategy


def advance_epoch(DFX_OFT, streamer, gauge, deploy_account, multisig_1):
    fastforward_chain_weeks(num_weeks=1, delta=10)
    DFX_OFT.transfer(
        streamer, 1e23, {"from": deploy_account, "gas_price": gas_strategy}
    )
    streamer.notify_reward_amount(
        DFX_OFT, {"from": multisig_1, "gas_price": gas_strategy}
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
    print(f"User available rewards: {available_rewards/1e18}")
    print(f"User claimed rewards: {claimed_rewards/1e18}")
    print(f"User balance: {DFX_OFT.balanceOf(deploy_account)/1e18}")
