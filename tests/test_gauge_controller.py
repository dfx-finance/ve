# References:
# 1. https://github.com/curvefi/curve-dao-contracts/blob/master/tests/integration/GaugeController/test_vote_weight.py
from brownie import chain, history
from brownie.network.gas.strategies import LinearScalingStrategy
from brownie.test import given, strategy
from hypothesis import settings
import pytest

import addresses

WEEK = 86400 * 7
YEAR = 86400 * 365

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('80 gwei', '250 gwei', 4.3)


# handle setup logic required for each unit test
@pytest.fixture(scope='module', autouse=True)
def setup(dfx, gauge_controller, voting_escrow, three_gauges, master_account, user_accounts):
    # Setup gauges
    default_gauge_weight = 0

    gauge_controller.add_type(
        'Liquidity', 1e18, {'from': master_account, 'gas_price': gas_strategy})
    for gauge in three_gauges:
        gauge_controller.add_gauge(
            gauge, default_gauge_weight, {'from': master_account, 'gas_price': gas_strategy})

    # Distribute coins
    master_account.transfer(addresses.DFX_OWNER, '10 ether',
                            gas_price=gas_strategy)
    dfx.mint(master_account, 10 * 10e24,
             {'from': addresses.DFX_OWNER, 'gas_price': gas_strategy})

    for acct in user_accounts:
        dfx.transfer(acct, 10e23,
                     {'from': master_account, 'gas_price': gas_strategy})
        dfx.approve(voting_escrow, 10e24,
                    {'from': acct, 'gas_price': gas_strategy})


# @given(
#     st_deposits=strategy("uint256[3]", min_value=1e21, max_value=1e23),
#     st_length=strategy("uint256[3]", min_value=52, max_value=100),
#     st_votes=strategy("uint[2][3]", min_value=0, max_value=5)
# )
# # strategy will run this test 50(?) times by default, at least 3 is necessary to generate non-0 values
# @settings(max_examples=3)
def test_gauge_weight_vote(gauge_controller, voting_escrow, three_gauges, user_accounts):
    '''
    Test that gauge weights correctly adjust over time.

    Strategies
    ---------
    st_deposits : [int, int, int]
        Number of coins to be deposited per account
    st_length : [int, int, int]
        Policy duration in weeks    
    st_votes : [(int, int), (int, int), (int, int)]
        (vote for gauge 0, vote for gauge 1) for each account, in units of 10%

    TODO: Curve tests simulate 3 user accounts whereas this currently only performs 1. Add
          additional accounts when 1 is working successfully.
    '''
    # Provide default values when decorator strategy is commented out
    st_deposits = [1000000000000000000079,
                   1000000000000000000150, 1000000000000000008880]
    st_length = [58, 87, 86]
    st_votes = [[4, 3], [1, 4], [0, 3]]

    # Init 10 s before the week change
    t0 = chain.time()
    t1 = (t0 + 2 * WEEK) // WEEK * WEEK - 10
    chain.sleep(t1 - t0)
    print('Original chain time:', t0)
    print('New chain time:', chain.time())

    # Deposit for voting
    timestamp = t1
    for i, acct in enumerate(user_accounts):
        voting_escrow.create_lock(
            st_deposits[i], timestamp + (st_length[i] * WEEK), {'from': acct, 'gas_price': gas_strategy})

    # Place votes in bps (10000 = 100.00%)
    votes = []
    for i, acct in enumerate(user_accounts):
        votes.append([x * 1000 for x in st_votes[i]])
        # Use remainder of 100.00% on last vote(?)
        # Source comment: "XXX what if votes are not used up to 100%?"
        votes[-1].append(10000 - sum(votes[-1]))

        for x in range(3):
            gauge_controller.vote_for_gauge_weights(
                three_gauges[x], votes[-1][x], {'from': acct, 'gas_price': gas_strategy})

    # Vote power assertions - everyone used all voting power
    for acct in user_accounts:
        assert gauge_controller.vote_user_power(acct) == 10000

    # Calculate slope data, build model functions for calcuating max duration and theoretical weight
    slope_data = []
    for i, acct in enumerate(user_accounts):
        initial_bias = voting_escrow.get_last_user_slope(
            acct) * (voting_escrow.locked(acct)[1] - timestamp)
        duration = (timestamp + 8 * WEEK) // WEEK * \
            WEEK  # endtime rounded down to whole weeks
        slope_data.append((initial_bias, duration))

    max_duration = max(duration for _, duration in slope_data)

    def models(idx, relative_time):
        bias, duration = slope_data[idx]
        return max(bias * (1 - relative_time * max_duration / duration), 0)

    # Advance clock a month at a time and compare theoretical weight to actual weight
    chain.sleep(WEEK * 4)
    # chain.mine()  # breaks ganache-cli with infinite "eth_getTransactionCount" calls

    # while history[-1].timestamp < timestamp + 1.5 * max_duration:
    for i in range(3):
        gauge_controller.checkpoint_gauge(
            three_gauges[i], {'from': user_accounts[2], 'gas_price': gas_strategy})

    # % of duration into lock (rounded down to latest epoch week) / max. lock duration
    relative_time = (history[-1].timestamp // WEEK *
                     WEEK - timestamp) / max_duration
    print('Relative time:', relative_time)

    weights = [gauge_controller.gauge_relative_weight(
        three_gauges[i]) / 1e18 for i in range(3)]
    if relative_time < 1:
        theoretical_weights = [
            sum((votes[i][0] / 10000) * models(i, relative_time)
                for i in range(3)),
            sum((votes[i][1] / 10000) * models(i, relative_time)
                for i in range(3)),
            sum((votes[i][2] / 10000) * models(i, relative_time)
                for i in range(3)),
        ]
        theoretical_weights = [
            w and (w / sum(theoretical_weights)) for w in theoretical_weights
        ]
    else:
        theoretical_weights = [0] * 3

    print(relative_time, weights, theoretical_weights)
    if relative_time != 1:
        for i in range(3):
            assert(
                abs(weights[i] - theoretical_weights[i])
                <= (history[-1].timestamp - timestamp) / WEEK + 1
            )

    chain.sleep(WEEK * 4)
