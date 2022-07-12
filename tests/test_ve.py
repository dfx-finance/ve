from argparse import ZERO_OR_MORE
from brownie import ZERO_ADDRESS, chain
from brownie.network.gas.strategies import LinearScalingStrategy
import pytest

import addresses

WEEK = 86400 * 7
DEFAULT_GAUGE_TYPE = 0  # Ethereum stableswap pools

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('30 gwei', '250 gwei', 1.3)

@pytest.fixture(scope='module', autouse=True)
def setup(dfx, gauge_controller, three_liquidity_gauges_v4, voting_escrow, master_account, user_accounts, mock_lp_tokens, dfx_distributor):
    # Setup Layout
    # 1. veDFX.sol (from veFactory) - already deployed on mainnet block 14724071
    # 2. veBoostProxy.vy - conftest.py
    # 3. GaugeController.py - conftest.py
    max_uint256 = 115792089237316195423570985008687907853269984665640564039457584007913129639935
    gauge_controller.add_type(
        'Liquidity', 1e18, {'from': master_account, 'gas_price': gas_strategy})

    for gauge in three_liquidity_gauges_v4:
        gauge_controller.add_gauge(
            gauge, DEFAULT_GAUGE_TYPE, {'from': master_account, 'gas_price': gas_strategy}
        )

    # Give some users DFX tokens to lock into the veDFX contracts
    for user in user_accounts:
        print(user)
        # mint some DFX
        dfx.mint(user, 100_000e18, {'from': addresses.DFX_OWNER, 'gas_price': gas_strategy})
        # approval
        dfx.approve(voting_escrow, max_uint256, {'from': user, 'gas_price': gas_strategy})

    # Fund distributor with DFX tokens
    dfx.mint(dfx_distributor, 100_000_000e18, {'from': addresses.DFX_OWNER, 'gas_price': gas_strategy})


def test_distributor(dfx_distributor, gauge_controller, user_accounts, master_account, voting_escrow, three_liquidity_gauges_v4):
    t0 = chain.time()
    t1 = (t0 + 2 * WEEK) // WEEK * WEEK - 10
    chain.sleep(t1 - t0)
    # Deposit 
    timestamp = t1
    st_deposits = [1000e18 + 79, 1000e18 + 180, 1000e18 + 888]
    st_length = [52, 52, 52]

    # for i, user in enumerate(user_accounts):
    # print(dfx.balanceOf(user_accounts[0]))
    # print(dfx.balanceOf(user_accounts[1]))
    # print(dfx.balanceOf(user_accounts[2]))
    voting_escrow.create_lock(
        st_deposits[0],
        timestamp + (st_length[0] * WEEK),
        {'from': user_accounts[0], 'gas_price': gas_strategy}
    )

    # voting_escrow.create_lock(
    #     st_deposits[1],
    #     timestamp + (st_length[1] * WEEK),
    #     {'from': user_accounts[1], 'gas_price': gas_strategy}
    # )
    
    # Vote 
    st_votes = [[4, 3], [1, 4], [0, 3]]
    votes = []
    
    
    # for i, acct in enumerate(user_accounts):
    # votes.append([x * 1000 for x in st_votes[]])
        # Use remainder of 100.00% on last vote(?)
        # Source comment: "XXX what if votes are not used up to 100%?"
    # votes[-1].append(10000 - sum(votes[-1]))

    
    gauge_controller.vote_for_gauge_weights(three_liquidity_gauges_v4[0], 10000, {'from': user_accounts[0], 'gas_price': gas_strategy})
    dfx_distributor.distributeRewardToMultipleGauges(
        [three_liquidity_gauges_v4[0]],
        {'from': user_accounts[0], 'gas_price': gas_strategy}
    )

# def test_veboost(dfx, voting_escrow, veboost_proxy, user_accounts):
#     user1 = user_accounts[1]
#     user2 = user_accounts[2]
#     max_uint256 = 115792089237316195423570985008687907853269984665640564039457584007913129639935

#     # mint some dfx 
#     dfx.mint(user1, 100e18, {'from': addresses.DFX_OWNER, 'gas_price': gas_strategy})
#     dfx.mint(user2, 100e18, {'from': addresses.DFX_OWNER, 'gas_price': gas_strategy})

#     # approval
#     dfx.approve(voting_escrow, max_uint256, {'from': user1, 'gas_price': gas_strategy})
#     dfx.approve(voting_escrow, max_uint256, {'from': user2, 'gas_price': gas_strategy})
    
    # lock into veDfx
    # 4 years
    # voting_escrow.create_lock(100e18, 1720744950, {'from': user1, 'gas_price': gas_strategy})
    # 2 years
    # voting_escrow.create_lock(100e18, 1720745007, {'from': user2, 'gas_price': gas_strategy})

    # user1_voting_power = veboost_proxy.adjusted_balance_of(user1)
    # user2_voting_power = veboost_proxy.adjusted_balance_of(user2)

    # print(user1_voting_power)
    # print(user2_voting_power)