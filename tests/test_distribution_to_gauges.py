#!/usr/bin/env python
import brownie
from datetime import datetime
import pytest

from utils.chain import fastforward_chain, gas_strategy
from utils.constants import EMISSION_RATE
from utils.gauges import setup_distributor, setup_gauge_controller
from utils.testing.token import fund_multisig


# handle setup logic required for each unit test
@pytest.fixture(scope='module', autouse=True)
def setup(dfx, gauge_controller, three_liquidity_gauges_v4, distributor, master_account, new_master_account):
    fund_multisig(master_account)

    # setup gauges and distributor
    setup_gauge_controller(
        gauge_controller, three_liquidity_gauges_v4, master_account)

    # Params:
    # - reward token
    # - distributor contract
    # - account from which to mint and provide rewards to distributor contract
    # - account which administers the distributor contract
    # - rate dependent on tokens available and weekly reduction (see spreadsheet)
    setup_distributor(dfx, distributor, master_account,
                      new_master_account, EMISSION_RATE)


@pytest.fixture(scope='module', autouse=True)
def teardown():
    yield
    brownie.chain.reset()


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
        fastforward_chain(num_weeks=1, delta=0)

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
