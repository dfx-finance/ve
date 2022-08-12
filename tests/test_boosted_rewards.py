#!/usr/bin/env python
from brownie import accounts, chain
import brownie
import pytest

import addresses
from utils import fastforward_chain, fund_multisig, mint_dfx, gas_strategy
from utils_gauges import deposit_lp_tokens, setup_distributor, setup_gauge_controller
from utils_ve import deposit_to_ve, submit_ve_vote, EMISSION_RATE, WEEK


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


def test_multi_user_stake(dfx, mock_lp_tokens, voting_escrow, three_liquidity_gauges_v4, gauge_controller, distributor, master_account):
    # 1. rewards are not claimed between rounds during test and therefore expected to accumulate
    # 2. expected rewards floored to nearest int value (whole DFX tokens) to allow for small variation between mining times
    expected = [
        # small difference for epoch 1 because ve deposit and voting hours before epoch change
        (1, 1607, 1599),
        (2, 10718, 5243),
        (3, 17485, 7950),
        (4, 24199, 10636),
        (5, 30861, 13301),
    ]

    # two random users
    user_0 = accounts[4]
    user_1 = accounts[5]

    # select the EUROC LP token and gauge for depositing
    euroc_usdc_lp = mock_lp_tokens[1]
    euroc_usdc_gauge = three_liquidity_gauges_v4[1]
    assert 'euroc' in euroc_usdc_lp.name().lower()
    assert 'euroc' in euroc_usdc_gauge.name().lower()

    # mint 10,000 lp tokens for the users
    lp_amount = 10e21
    euroc_usdc_lp.mint(user_0, lp_amount, {
        'from': master_account, 'gas_price': gas_strategy})
    euroc_usdc_lp.mint(user_1, lp_amount, {
        'from': master_account, 'gas_price': gas_strategy})
    assert euroc_usdc_lp.balanceOf(user_0) == lp_amount
    assert euroc_usdc_lp.balanceOf(user_1) == lp_amount

    # deposit tokens to gauge
    deposit_lp_tokens(euroc_usdc_lp, euroc_usdc_gauge, user_0)
    deposit_lp_tokens(euroc_usdc_lp, euroc_usdc_gauge, user_1)

    # for user0 only, mint 250,000 dfx and lock it for 4 years
    dfx_amount = 250000 * 1e18
    mint_dfx(dfx, dfx_amount, user_0)
    assert dfx.balanceOf(user_0) / 10**dfx.decimals() == 250000

    # set chain to 10s before the week change (during epoch 1) and
    # distribute available reward to gauges
    t0 = chain.time()
    assert distributor.miningEpoch() == 0

    t1 = (t0 + 2 * WEEK) // WEEK * WEEK - 10
    chain.sleep(t1 - t0)
    distributor.distributeRewardToMultipleGauges(
        three_liquidity_gauges_v4, {'from': master_account, 'gas_price': gas_strategy})
    assert distributor.miningEpoch() == 1

    # advance chain to 5h10s before next epoch change
    chain.sleep(WEEK - 5*60*60)
    t2 = chain.time()
    deposit_to_ve(dfx, voting_escrow, [user_0], [2.5e23], [208], t2)
    submit_ve_vote(gauge_controller, three_liquidity_gauges_v4,
                   [0, 10000, 0], user_0)

    # advance the chain slightly (4h) to test rewards immediate begin accumulating
    chain.sleep(4*60*60)

    # checkpoint necessary for calculating boost
    euroc_usdc_gauge.user_checkpoint(
        user_0, {'from': user_0, 'gas_price': gas_strategy})
    assert int(euroc_usdc_gauge.claimable_reward(
        user_0, addresses.DFX) // 1e18) == 1594  # ~1,594 DFX
    assert distributor.miningEpoch() == 1

    # 10s before next epoch (3) begins
    t3 = (t2 + WEEK) // WEEK * WEEK - 10
    fastforward_chain(t3 - t2)

    # test next 5 epochs between naked and boosted rewards
    for i in range(5):
        epoch, user0_rewards, user1_rewards = expected[i]
        assert distributor.miningEpoch() == epoch

        distributor.distributeRewardToMultipleGauges(
            three_liquidity_gauges_v4, {'from': master_account, 'gas_price': gas_strategy})

        # checkpoint for calculating boost
        euroc_usdc_gauge.user_checkpoint(
            user_0, {'from': user_0, 'gas_price': gas_strategy})
        euroc_usdc_gauge.user_checkpoint(
            user_1, {'from': user_1, 'gas_price': gas_strategy})

        assert int(euroc_usdc_gauge.claimable_reward(
            user_0, addresses.DFX) // 1e18) == user0_rewards
        assert int(euroc_usdc_gauge.claimable_reward(
            user_1, addresses.DFX) // 1e18) == user1_rewards
        fastforward_chain(WEEK)
