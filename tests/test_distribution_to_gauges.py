#!/usr/bin/env python
from datetime import datetime
import pytest

import brownie
from brownie.network.gas.strategies import LinearScalingStrategy

import utils

TOTAL_DFX_REWARDS = 1_000_000 * 1e18


# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('30 gwei', '250 gwei', 1.3)


# handle setup logic required for each unit test
@pytest.fixture(scope='module', autouse=True)
def setup(dfx, gauge_controller, three_liquidity_gauges_v4, distributor, master_account, new_master_account):
    utils.fund_multisig(master_account)
    utils.setup_gauge_controller(
        gauge_controller, three_liquidity_gauges_v4, master_account)

    # Supply distributor contract with rewards
    utils.mint_dfx(dfx, TOTAL_DFX_REWARDS, master_account)

    # Distribute rewards to the distributor contract
    utils.send_dfx(dfx, TOTAL_DFX_REWARDS, master_account, distributor)

    # Turn on distributions to gauges
    distributor.toggleDistributions(
        {'from': new_master_account, 'gas_price': gas_strategy})

    # Set rate to distribute 1,000,000 rewards (see spreadsheet)
    distributor.setRate(
        1.2842402e16, {'from': new_master_account, 'gas_price': gas_strategy})


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

    for _ in range(10):
        utils.fastforward_chain(utils.WEEK)

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
