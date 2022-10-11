#!/usr/bin/env python
from math import isclose
import brownie
from brownie import accounts
import pytest

from utils.apr import (
    distribute_to_gauges,
    calc_boosted_apr,
    claim_rewards,
    claimable_rewards,
    get_euro_usdc_gauge,
    mint_lp_tokens,
)
from utils.chain import fastforward_chain, gas_strategy
from utils.constants import EMISSION_RATE
from utils.gauges import deposit_lp_tokens, setup_distributor, setup_gauge_controller
from utils.testing import addresses
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


def compare_available_rewards(dfx, gauge, gauge_balance, users, expected_rewards, expected_sizes=None):
    available_rewards = claimable_rewards(dfx, gauge, users)
    # Compare user's amount of rewards
    for i, user in enumerate(users):
        assert isclose(available_rewards[user],
                       expected_rewards[i], abs_tol=1e16)
    # Compare user's share (as 0.0-1.0 ratio) of rewards
    if expected_sizes:
        for i, user in enumerate(users):
            assert isclose(available_rewards[user] /
                           gauge_balance, expected_sizes[i], abs_tol=1e-4)
    return available_rewards


def compare_claimed_rewards(gauge, users, signer_account, expected_rewards):
    rewards = claim_rewards(gauge, addresses.DFX, users, signer_account)
    for i, user in enumerate(users):
        assert isclose(rewards[user], expected_rewards[i], abs_tol=1e16)
    return rewards


def test_unboosted_apr(dfx, mock_lp_tokens, distributor, voting_escrow, veboost_proxy, three_liquidity_gauges_v4, master_account):
    # two random users
    user_0 = accounts[4]
    user_1 = accounts[5]

    # select the EUROC/USDC LP token and gauge for depositing
    euroc_usdc_lp, euroc_usdc_gauge = get_euro_usdc_gauge(
        mock_lp_tokens, three_liquidity_gauges_v4)

    # 1. Test that expected amount of LP tokens are minted
    mint_lp_tokens(euroc_usdc_lp, [user_0, user_1], master_account)

    # 2a. Test that epoch 0 is the current epoch
    # fast-forward to 5s after epoch 0 start
    fastforward_chain(num_weeks=1, delta=5)
    assert distributor.miningEpoch() == 0

    # 2b. Test that gauge distributions at beginning of epoch 0 results in the expected amount of rewards
    # at start of epoch 0.
    gauge_reward_balances = distribute_to_gauges(dfx,
                                                 distributor,
                                                 three_liquidity_gauges_v4,
                                                 master_account,
                                                 {euroc_usdc_gauge: 3207448777992851545592})
    assert distributor.miningEpoch() == 1

    # 2c. Deposit LP tokens into the gauge for epoch 0 rewards.
    deposit_lp_tokens(euroc_usdc_lp, euroc_usdc_gauge, user_0)
    deposit_lp_tokens(euroc_usdc_lp, euroc_usdc_gauge, user_1)

    # 3. Fast-forward until the very end of epoch 1 and claim rewards. Check available rewards, claimed rewards
    # and unboosted APR
    fastforward_chain(num_weeks=1, delta=-10)
    available_rewards = compare_available_rewards(dfx,
                                                  euroc_usdc_gauge,
                                                  gauge_reward_balances[euroc_usdc_gauge],
                                                  [user_0, user_1],
                                                  expected_rewards=[
                                                      1603679310764592004000, 1603668704121807640000],
                                                  expected_sizes=[0.5, 0.5])
    compare_claimed_rewards(euroc_usdc_gauge,
                            [user_0, user_1],
                            master_account,
                            expected_rewards=[1603681962425288096000, 1603671355782503732000])
    apr = calc_boosted_apr(voting_escrow, veboost_proxy,
                           euroc_usdc_gauge, user_0, available_rewards['combined'])
    assert isclose(apr, 1.4611242790681405, abs_tol=1e-4)

    # 4. Test what happens when no rewards are during the epoch. Does the APR immediately fall to 0?
    fastforward_chain(num_weeks=2, delta=-10)
    distributor.updateMiningParameters(
        {'from': master_account, 'gas_price': gas_strategy})
    assert distributor.miningEpoch() == 2
    available_rewards = compare_available_rewards(dfx,
                                                  euroc_usdc_gauge,
                                                  gauge_reward_balances[euroc_usdc_gauge],
                                                  [user_0, user_1],
                                                  expected_rewards=[
                                                      42426571137464000, 39774910441376000])
    apr = calc_boosted_apr(voting_escrow, veboost_proxy,
                           euroc_usdc_gauge, user_0, available_rewards['combined'])
    assert isclose(apr, 4.41e-5, abs_tol=1e-1)

    # 5. Fast-forward to start of epoch 3, distribute gauge rewards and check that APR is back to expected value
    fastforward_chain(num_weeks=1, delta=10)
    distributor.updateMiningParameters(
        {'from': master_account, 'gas_price': gas_strategy})
    assert distributor.miningEpoch() == 3
    gauge_reward_balances = distribute_to_gauges(dfx,
                                                 distributor,
                                                 three_liquidity_gauges_v4,
                                                 master_account,
                                                 {})

    available_rewards = claimable_rewards(
        dfx, euroc_usdc_gauge, [user_0, user_1])
    apr = calc_boosted_apr(voting_escrow, veboost_proxy,
                           euroc_usdc_gauge, user_0, available_rewards['combined'])
    assert isclose(apr, 2.8883305368143133, abs_tol=1e-5)

    # Fast-forward until 10s before end of epoch 3
    fastforward_chain(num_weeks=1, delta=-10)
    compare_available_rewards(dfx,
                              euroc_usdc_gauge,
                              gauge_reward_balances[euroc_usdc_gauge],
                              [user_0, user_1],
                              expected_rewards=[3170101193477298720000, 3170098541816602632000])
    compare_claimed_rewards(euroc_usdc_gauge,
                            [user_0, user_1],
                            master_account,
                            expected_rewards=[4773791049257621272000, 4773785684309175268000])
