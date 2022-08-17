#!/usr/bin/env python
import brownie
from brownie import accounts
from datetime import datetime
import pytest

import addresses
from utils import fund_multisig, gas_strategy
from utils_chain import fastforward_chain
from utils_gauges import deposit_lp_tokens, setup_distributor, setup_gauge_controller
from utils_ve import EMISSION_RATE, WEEK

DFX_PRICE = 0.554326 * 1e18
LP_PRICE = 1.00452 * 1e18


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
    print("now (setup):", datetime.fromtimestamp(brownie.chain.time()))
    print("setup epoch start (setup):", datetime.fromtimestamp(
        distributor.startEpochTime()))


@pytest.fixture(scope='module', autouse=True)
def teardown():
    yield
    brownie.chain.reset()


# Print current chain time and epoch
def log_times(distributor, stage):
    now = brownie.chain.time()
    print(f"{stage} -- chain time:", datetime.fromtimestamp(now))
    print(f"{stage} -- current epoch:", distributor.miningEpoch())


# Distribute rewards to all registered gauges and return balances
def distribute_to_gauges(dfx, distributor, gauges, account, assertions):
    distributor.distributeRewardToMultipleGauges(
        gauges, {'from': account, 'gas_price': gas_strategy})
    balances = {g: dfx.balanceOf(g) for g in gauges}
    for g, expected_balance in assertions.items():
        assert balances[g] == expected_balance
    return balances


# Fetch relative weights of all registered gauges
def gauge_relative_weights(gauge_controller, gauges):
    weights = {}
    for g in gauges:
        weights[g] = gauge_controller.gauge_relative_weight(g)
    return weights


# Fetch the available rewards to claim for all users
def claimable_rewards(gauge, reward_address, users):
    rewards = {}
    total = 0
    for u in users:
        amount = gauge.claimable_reward(u, reward_address)
        rewards[u] = amount
        total += amount
    rewards['combined'] = total
    return rewards


def claim_rewards(gauge, reward_address, users, signer_account):
    rewards = {}
    total = 0
    for u in users:
        gauge.claim_rewards(
            u, {'from': signer_account, 'gas_price': gas_strategy})
        amount = gauge.claimed_reward(u, reward_address)
        rewards[u] = amount
        total += amount
    rewards['combined'] = total
    return rewards


def calc_theoretical_rewards(distributor, gauge_weight):
    global_rewards = distributor.rate() * WEEK
    gauge_rewards = global_rewards * gauge_weight / 1e18
    return global_rewards, gauge_rewards


def calc_apr(dfx, lp_token, distributor, gauge, gauge_weight):
    gauge_reward_balance = dfx.balanceOf(gauge)
    _, theoretical_gauge_rewards = calc_theoretical_rewards(
        distributor, gauge_weight)

    lp_balance = lp_token.balanceOf(gauge)
    lp_usd = lp_balance * LP_PRICE

    # rewards = min(gauge_reward_balance, theoretical_gauge_rewards)
    rewards = gauge_reward_balance

    rewards_usd = rewards * DFX_PRICE
    yearly_rewards_usd = rewards_usd * 52
    # print(rewards / 1e18)
    # print(yearly_rewards_usd / 1e36, lp_usd / 1e36)
    apr = yearly_rewards_usd / lp_usd

    # print("LP tokens in gauge:", lp_balance)
    # print("LP value (USD)", lp_usd / 1e36)
    # print("Rewards value (USD):", rewards_usd / 1e36)
    # print("Yearly rewards value (USD at current rate):", yearly_rewards_usd / 1e36)
    # print("APR", apr)
    return apr

# def _apr(voting_escrow, veboost_proxy, gauge, account):
#     TOKENLESS_PRODUCTION = 40  # as hardcoded in contract
#     gauge_lp_balance = gauge.balanceOf(account)
#     voting_balance = veboost_proxy.adjusted_balance_of(account)
#     voting_total = voting_escrow.totalSupply()

#     lim = gauge_lp_balance * TOKENLESS_PRODUCTION / 100
#     if voting_total > 0:
#         lim = gauge_lp_balance * voting_balance / \
#             voting_total * (100 - TOKENLESS_PRODUCTION) / 100

#     print("calc'd limit:", lim)
#     lim = min(gauge_lp_balance, lim)
#     return lim


def test_two_user_apr(dfx, mock_lp_tokens, voting_escrow, gauge_controller, distributor, veboost_proxy, three_liquidity_gauges_v4, master_account):
    # two random users
    user_0 = accounts[4]
    user_1 = accounts[5]

    # select the EUROC LP token and gauge for depositing
    euroc_usdc_lp = mock_lp_tokens[1]
    euroc_usdc_gauge = three_liquidity_gauges_v4[1]
    assert 'euroc' in euroc_usdc_lp.name().lower()
    assert 'euroc' in euroc_usdc_gauge.name().lower()

    # 1. Test that expected amount of LP tokens are minted
    # mint 10,000 lp tokens for the users
    print("1 -- Mint LP tokens")
    log_times(distributor, "1")
    lp_amount = 10e21
    euroc_usdc_lp.mint(user_0, lp_amount, {
        'from': master_account, 'gas_price': gas_strategy})
    euroc_usdc_lp.mint(user_1, lp_amount, {
        'from': master_account, 'gas_price': gas_strategy})
    assert euroc_usdc_lp.balanceOf(user_0) == lp_amount
    assert euroc_usdc_lp.balanceOf(user_1) == lp_amount

    # 2a. Test that epoch 0 is the current epoch
    # fast-forward to 5s after epoch 0 start
    print("\n2a -- Fast-forward until 5s after epoch 1 starts")
    fastforward_chain(num_weeks=1, delta=5)
    assert distributor.miningEpoch() == 0
    print("2a -- Epoch start time:", datetime.fromtimestamp(
        distributor.startEpochTime()))
    # 2b. Test that gauge distributions at beginning of epoch 0 results in the expected amount of rewards
    # at start of epoch 0.
    gauge_reward_balances = distribute_to_gauges(dfx,
                                                 distributor,
                                                 three_liquidity_gauges_v4,
                                                 master_account,
                                                 {euroc_usdc_gauge: 3207448777992851545592})
    assert distributor.miningEpoch() == 1
    log_times(distributor, "2a")
    print("2b -- contract bal (DFX):",
          gauge_reward_balances[euroc_usdc_gauge] / 1e18)
    # 2c. Deposit LP tokens into the gauge for epoch 0 rewards.
    deposit_lp_tokens(euroc_usdc_lp, euroc_usdc_gauge, user_0)
    deposit_lp_tokens(euroc_usdc_lp, euroc_usdc_gauge, user_1)

    # 3. Fast-forward until the very end of epoch 1 and claim rewards. Check theoretical vs
    # actually claimed rewards and calculated unboosted APR
    print("\n3 -- Fast-forward until 10s before end of epoch 1")
    fastforward_chain(num_weeks=1, delta=-10)
    log_times(distributor, "3")

    # Fetch the relative weight for each gauge
    gauge_weights = gauge_relative_weights(
        gauge_controller, three_liquidity_gauges_v4)

    # Theoretical rewards:
    theoretical_global_rewards, theoretical_gauge_rewards = calc_theoretical_rewards(
        distributor, gauge_weights[euroc_usdc_gauge])
    gauge_balance = gauge_reward_balances[euroc_usdc_gauge]
    apr = calc_apr(dfx, euroc_usdc_lp, distributor, euroc_usdc_gauge,
                   gauge_weights[euroc_usdc_gauge])
    # Actually claimed rewards:
    available_rewards = claimable_rewards(
        euroc_usdc_gauge, addresses.DFX, [user_0, user_1])
    rewards = claim_rewards(euroc_usdc_gauge, addresses.DFX, [
                            user_0, user_1], master_account)

    print("3 -- Calculated global rewards:", theoretical_global_rewards / 1e18)
    print("3 -- Calculated gauge (EUROC/USDC) rewards:",
          theoretical_gauge_rewards / 1e18)
    print(
        f"3 -- user0 available reward (DFX): {available_rewards[user_0]/1e18} ({available_rewards[user_0]/gauge_balance})")
    print(
        f"3 -- user1 available reward (DFX): {available_rewards[user_1]/1e18} ({available_rewards[user_1]/gauge_balance})")
    print(
        f"3 -- user0 reward (DFX): {rewards[user_0]/1e18} ({rewards[user_0]/gauge_balance})")
    print(
        f"3 -- user1 reward (DFX): {rewards[user_1]/1e18} ({rewards[user_1]/gauge_balance})")
    print("3 -- Combined claimed reward (DFX):",
          rewards['combined'] / 1e18)
    print("3 -- Ratio of total possible rewards claimed by users:",
          rewards['combined']/theoretical_global_rewards)
    print("3 -- APR:", apr * 100)

    # 4. Test what happens when no rewards are during the epoch. Does the APR immediately fall to 0? (Yes)
    print("\n4 -- Fast-forward until 10s before end of epoch 2 (no rewards added for epoch)")
    fastforward_chain(num_weeks=2, delta=-10)
    distributor.updateMiningParameters(
        {'from': master_account, 'gas_price': gas_strategy})
    log_times(distributor, "4")

    available_rewards = claimable_rewards(
        euroc_usdc_gauge, addresses.DFX, [user_0, user_1])
    print("4 -- user0 available reward:", available_rewards[user_0] / 1e18)
    print("4 -- user1 available reward:", available_rewards[user_1] / 1e18)
    # assert available_rewards[user_0] == 24051758316424000
    # assert available_rewards[user_1] == 21379340725712000
    apr = calc_apr(dfx, euroc_usdc_lp, distributor, euroc_usdc_gauge,
                   gauge_weights[euroc_usdc_gauge])
    print("4 -- APR:", apr * 100)

    # 5. Fast-forward to start of epoch 4, distribute gauge rewards and check that APR is back to expected value
    print("\n5 -- Fast-forward until 10s after epoch 4 (rewards + back rewards added)")
    fastforward_chain(num_weeks=1, delta=5)
    distributor.updateMiningParameters(
        {'from': master_account, 'gas_price': gas_strategy})
    log_times(distributor, "5")
    gauge_reward_balances = distribute_to_gauges(dfx,
                                                 distributor,
                                                 three_liquidity_gauges_v4,
                                                 master_account,
                                                 {})
    apr = calc_apr(dfx, euroc_usdc_lp, distributor, euroc_usdc_gauge,
                   gauge_weights[euroc_usdc_gauge])
    print("5 -- APR:", apr * 100)
    print("5 -- Fast-forward until 10s before end of epoch 3")
    fastforward_chain(num_weeks=1, delta=-10)
    available_rewards = claimable_rewards(
        euroc_usdc_gauge, addresses.DFX, [user_0, user_1])
    rewards = claim_rewards(euroc_usdc_gauge, addresses.DFX, [
                            user_0, user_1], master_account)
    print("5 -- Available round rewards:",
          available_rewards[user_0] / 1e18, available_rewards[user_1] / 1e18)
    print("5 -- Total rewards claimed:",
          rewards[user_0] / 1e18, rewards[user_1] / 1e18)
