# References:
# 1. https://github.com/curvefi/curve-dao-contracts/blob/master/tests/integration/GaugeController/test_vote_weight.py
from brownie import chain, history
import pytest

from utils import fund_multisig, mint_dfx, send_dfx, gas_strategy, WEEK
from utils_gauges import setup_gauge_controller
from utils_ve import deposit_to_ve, submit_ve_votes, calculate_ve_slope_data


# handle setup logic required for each unit test
@pytest.fixture(scope='module', autouse=True)
def setup(dfx, gauge_controller, three_liquidity_gauges_v4, master_account, user_accounts):
    fund_multisig(master_account)
    setup_gauge_controller(
        gauge_controller, three_liquidity_gauges_v4, master_account)

    # Distribute coins
    mint_dfx(dfx, 1e24, master_account)

    # Move 50k DFX to each user wallet
    for acct in user_accounts:
        send_dfx(dfx, 5e22, master_account, acct)


@pytest.fixture(scope='module', autouse=True)
def teardown(voting_escrow, user_accounts):
    yield

    # Withdraw all tokens from lock
    print("\nWithdrawing...")
    for i, acct in enumerate(user_accounts):
        print(f"Withdraw {i} - {acct}")
        voting_escrow.withdraw({'from': acct, 'gas_price': gas_strategy})


# @given(
#     st_deposits=strategy("uint256[3]", min_value=1e21, max_value=1e23),
#     st_length=strategy("uint256[3]", min_value=52, max_value=100),
#     st_votes=strategy("uint[2][3]", min_value=0, max_value=5)
# )
# # strategy will run this test 50(?) times by default, at least 3 is necessary to generate non-0 values
# @settings(max_examples=3)
def test_gauge_weight_vote(dfx, gauge_controller, voting_escrow, three_liquidity_gauges_v4, user_accounts):
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
    deposit_to_ve(dfx, voting_escrow, user_accounts,
                  st_deposits, st_length, timestamp)

    # Place votes in bps (10000 = 100.00%)
    votes = submit_ve_votes(
        gauge_controller, three_liquidity_gauges_v4, user_accounts, st_votes)

    # Vote power assertions - everyone used all voting power
    for acct in user_accounts:
        assert gauge_controller.vote_user_power(acct) == 10000

    # Calculate slope data, build model functions for calcuating max duration and theoretical weight
    slope_data = calculate_ve_slope_data(
        voting_escrow, user_accounts, st_length, timestamp)

    max_duration = max(duration for _, duration in slope_data)

    def models(idx, relative_time):
        bias, duration = slope_data[idx]
        return max(bias * (1 - relative_time * max_duration / duration), 0)

    # Advance clock a month at a time and compare theoretical weight to actual weight
    chain.sleep(WEEK * 4)
    chain.mine()  # breaks ganache-cli with infinite "eth_getTransactionCount" calls

    while history[-1].timestamp < timestamp + 1.5 * max_duration:
        for i in range(3):
            gauge_controller.checkpoint_gauge(
                three_liquidity_gauges_v4[i], {'from': user_accounts[2], 'gas_price': gas_strategy})

        # % of duration into lock (rounded down to latest epoch week) / max. lock duration
        relative_time = (history[-1].timestamp // WEEK *
                         WEEK - timestamp) / max_duration

        weights = [gauge_controller.gauge_relative_weight(
            three_liquidity_gauges_v4[i]) / 1e18 for i in range(3)]
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

        print((
            f'Relative time: {relative_time}'
            f'\n\tWeights:\t\t{weights}'
            f'\n\tTheoretical Weights:\t{theoretical_weights}'
        ))
        if relative_time != 1:
            for i in range(3):
                assert(
                    abs(weights[i] - theoretical_weights[i])
                    <= (history[-1].timestamp - timestamp) / WEEK + 1
                )  # 1 s per week?

        chain.sleep(WEEK * 4)
        chain.mine()
