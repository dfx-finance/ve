#!/usr/bin/env python
from datetime import datetime
import pytest

from brownie import ZERO_ADDRESS, chain
import brownie
from brownie.network.gas.strategies import LinearScalingStrategy

import utils


# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('30 gwei', '250 gwei', 1.3)


# handle setup logic required for each unit test
@pytest.fixture(scope='module', autouse=True)
def setup(dfx, gauge_controller, three_liquidity_gauges_v4, distributor, master_account, new_master_account):
    utils.setup_gauges(
        gauge_controller, three_liquidity_gauges_v4, master_account)

    # Supply distributor contract with rewards
    total_rewards = 1_000_000 * 1e18
    utils.mint_dfx(dfx, total_rewards, master_account)

    # Distribute rewards to the distributor contract
    utils.send_dfx(dfx, total_rewards, master_account, distributor)

    # Turn on distributions to gauges
    distributor.toggleDistributions(
        {'from': new_master_account, 'gas_price': gas_strategy})

    # Set rate to distribute 1,000,000 rewards (see spreadsheet)
    distributor.setRate(
        1.2842402e16, {'from': new_master_account, 'gas_price': gas_strategy})


# def _cast_votes(dfx, gauge_controller, voting_escrow, gauges, master_account, user_accounts):
#     timestamp = chain.time()

#     # Move 50k DFX to each user wallet and approve for spending by Voting Escrow
#     total_rewards = 15e22
#     utils.mint_dfx(dfx, total_rewards, master_account)
#     for acct in user_accounts:
#         utils.send_dfx(dfx, 5e22, master_account, acct)
#         dfx.approve(voting_escrow, 5e22,
#                     {'from': acct, 'gas_price': gas_strategy})

#     # Provide default values when decorator strategy is commented out
#     st_deposits = [
#         5e22,
#         5e22,
#         5e22,
#     ]
#     st_length = [58, 87, 86]
#     st_votes = [[4, 3], [1, 4], [0, 3]]

#     utils.deposit_to_ve(voting_escrow, user_accounts,
#                         st_deposits, st_length, timestamp)

#     # Place votes in bps (10000 = 100.00%)
#     utils.submit_ve_votes(
#         gauge_controller, gauges, user_accounts, st_votes)

def _distribute_to_all_gauges(distributor, three_liquidity_gauges_v4, account):
    gauge_addresses = [g.address for g in three_liquidity_gauges_v4]

    tx = distributor.distributeRewardToMultipleGauges(
        gauge_addresses, {'from': account, 'gas_price': gas_strategy})

    logs = []
    rewards_distributed = tx.events['RewardDistributed']
    for reward in rewards_distributed:
        gauge_num = gauge_addresses.index(reward['gaugeAddr'])
        logs.append([gauge_num, reward['gaugeAddr'],
                    reward['rewardTally'] / 1e18])
    return logs


def test_distribute_rewards(dfx, gauge_controller, distributor, three_liquidity_gauges_v4, master_account, new_master_account):
    # artificially set weight on first and second gauges
    gauge_controller.change_gauge_weight(
        three_liquidity_gauges_v4[0], 1 * 1e18, {'from': master_account, 'gas_price': gas_strategy})
    gauge_controller.change_gauge_weight(
        three_liquidity_gauges_v4[1], 1.1 * 1e18, {'from': master_account, 'gas_price': gas_strategy})
    # gauge_controller.change_gauge_weight(
    #     three_liquidity_gauges_v4[2], 10000000000 * 1e18, {'from': master_account, 'gas_price': gas_strategy})

    # _cast_votes(dfx, gauge_controller, voting_escrow, three_liquidity_gauges_v4,
    #             master_account, user_accounts)

    for _ in range(10):
        # Advance chain clock
        brownie.chain.sleep(utils.WEEK)
        brownie.chain.mine()

        # Gauge distributions
        distribute_logs = _distribute_to_all_gauges(
            distributor, three_liquidity_gauges_v4, new_master_account)

        print("--- Logs")
        print("Epoch:", distributor.miningEpoch())

        print("Gauge Distributions:")
        for gauge_num, gauge_addr, amount in distribute_logs:
            print(f"\tGauge {gauge_num} ({gauge_addr}): {amount}")

        # checks
        print("Distributor balance:",  dfx.balanceOf(distributor) / 1e18)

        for gauge in three_liquidity_gauges_v4:
            print(f"{gauge.name()} balance:",  dfx.balanceOf(gauge) / 1e18)

        print("Relative weights:")
        for gauge in three_liquidity_gauges_v4:
            print(f"\t{gauge.name()}", gauge_controller.gauge_relative_weight(
                gauge.address) / 1e18)

        chain_time = brownie.chain.time()
        last_time_gauge_paid = distributor.lastTimeGaugePaid(
            three_liquidity_gauges_v4[0])
        print(
            f"Chain time: {chain_time} ({datetime.fromtimestamp(chain_time)})")
        print(
            f"Last time gauge paid: {last_time_gauge_paid} ({datetime.fromtimestamp(last_time_gauge_paid)})")
