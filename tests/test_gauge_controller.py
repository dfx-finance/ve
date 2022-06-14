# References:
# 1. https://github.com/curvefi/curve-dao-contracts/blob/master/tests/integration/GaugeController/test_vote_weight.py
from brownie import chain, history
from brownie.network.gas.strategies import LinearScalingStrategy
from brownie.test import given, strategy
import pytest

import addresses

WEEK = 86400 * 7
YEAR = 86400 * 365

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('40 gwei', '150 gwei', 1.3)


# handle setup logic required for each unit test
@pytest.fixture(scope='module', autouse=True)
def setup(dfx, gauge_controller, voting_escrow, three_gauges, master_account, user_accounts):
    # Setup gauges
    gauge0 = three_gauges[0]
    gauge0_weight = 0

    gauge_controller.add_type(
        'Liquidity', 10 ** 18, {'from': master_account, 'gas_price': gas_strategy})
    gauge_controller.add_gauge(
        gauge0, gauge0_weight, {'from': master_account, 'gas_price': gas_strategy})

    # Distribute coins
    master_account.transfer(addresses.DFX_OWNER, '10 ether',
                            gas_price=gas_strategy)
    dfx.mint(master_account, 10 * 10e18,
             {'from': addresses.DFX_OWNER, 'gas_price': gas_strategy})

    for acct in user_accounts:
        dfx.transfer(acct, 1 * 10e18,
                     {'from': master_account, 'gas_price': gas_strategy})
        dfx.approve(voting_escrow, 10e24,
                    {'from': acct, 'gas_price': gas_strategy})


# @given(
#     st_votes=strategy("uint[2][3]", min_value=0, max_value=5)
# )
def test_gauge_weight_vote(gauge_controller, voting_escrow, three_gauges, user_accounts):
    '''
    Test that gauge weights correctly adjust over time.

    Strategies
    ---------
    st_votes : [(int, int), (int, int), (int, int)]
        (vote for gauge 0, vote for gauge 1) for each account, in units of 10%

    TODO: Curve tests simulate 3 user accounts whereas this currently only performs 1. Add
          additional accounts when 1 is working successfully.
    '''
    # Init 10 s before the week change
    t0 = chain.time()
    t1 = (t0 + 2 * WEEK) // WEEK * WEEK - 10
    chain.sleep(t1 - t0)
    print('Original chain time:', t0)
    print('New chain time:', chain.time())

    timestamp = t1

    # Deposit for voting
    voting_escrow.create_lock(
        1 * 1e18, timestamp + 8 * WEEK, {'from': user_accounts[0], 'gas_price': gas_strategy})

    # Place votes in bps (10000 = 100.00%)
    gauge_controller.vote_for_gauge_weights(
        three_gauges[0], 10000, {'from': user_accounts[0], 'gas_price': gas_strategy})

    print('User voting power used:',
          gauge_controller.vote_user_power(user_accounts[0]))

    # Calculate slope data, build model functions for calcuating max duration and theoretical weight
    slope_data = []
    initial_bias = voting_escrow.get_last_user_slope(
        user_accounts[0]) * (voting_escrow.locked(user_accounts[0])[1] - timestamp)
    duration = (timestamp + 8 * WEEK) // WEEK * \
        WEEK  # endtime rounded down to whole weeks
    slope_data.append((initial_bias, duration))

    max_duration = max(duration for bias, duration in slope_data)

    def models(idx, relative_time):
        bias, duration = slope_data[idx]
        return max(bias * (1 - relative_time * max_duration / duration), 0)

    # Advance clock a month at a time and compare theoretical weight to actual weight
    chain.sleep(WEEK * 4)
    # chain.mine()  # breaks ganache-cli with infinite "eth_getTransactionCount" calls

    # while history[-1].timestamp < timestamp + 1.5 * max_duration:
    gauge0 = three_gauges[0]
    gauge_controller.checkpoint_gauge(
        gauge0, {'from': user_accounts[2], 'gas_price': gas_strategy})

    # % of duration into lock (rounded down to latest epoch week) / max. lock duration
    relative_time = (history[-1].timestamp // WEEK *
                     WEEK - timestamp) / max_duration
    print('Relative time:', relative_time)

    weight = gauge_controller.gauge_relative_weight(gauge0) / 1e18
    print('Gauge weight:', weight)
