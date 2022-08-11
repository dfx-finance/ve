#!/usr/bin/env python
from brownie import accounts, chain
import pytest

import addresses
from utils import fastforward_chain, fund_multisig, mint_dfx, gas_strategy, WEEK
from utils_gauges import deposit_lp_tokens, setup_distributor, setup_gauge_controller
from utils_ve import deposit_to_ve, submit_ve_vote


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
                      new_master_account, 1.2842402e16)


@pytest.fixture(scope='module', autouse=True)
def teardown(dfx, voting_escrow):
    yield

    # same two users
    user_0 = accounts[4]
    user_1 = accounts[5]

    # Withdraw all tokens from lock
    print("\nWithdrawing...")
    for i, acct in enumerate([user_0, user_1]):
        print(f"Withdraw {i} - {acct}")
        voting_escrow.withdraw({'from': acct, 'gas_price': gas_strategy})

    # Burn all DFX user balances
    burn_amt_0 = dfx.balanceOf(user_0)
    burn_amt_1 = dfx.balanceOf(user_1)
    dfx.transfer(addresses.DFX_MULTISIG, burn_amt_0, {
                 'from': user_0, 'gas_price': gas_strategy})
    dfx.transfer(addresses.DFX_MULTISIG, burn_amt_1, {
                 'from': user_1, 'gas_price': gas_strategy})


def test_multi_user_stake(dfx, mock_lp_tokens, voting_escrow, three_liquidity_gauges_v4, gauge_controller, distributor, master_account):
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

    # Init 10 s before the week change
    t0 = chain.time()
    timestamp = (t0 + WEEK) // WEEK * WEEK - 10
    deposit_to_ve(dfx, voting_escrow, [user_0], [2.5e23], [208], timestamp)

    submit_ve_vote(gauge_controller, three_liquidity_gauges_v4,
                   [0, 10000, 0], user_0)

    for i in range(5):
        euroc_usdc_gauge.user_checkpoint(
            user_0, {'from': user_0, 'gas_price': gas_strategy})

        distributor.distributeRewardToMultipleGauges(
            three_liquidity_gauges_v4, {'from': master_account, 'gas_price': gas_strategy})
        print(i, user_0, euroc_usdc_gauge.claimable_reward(
            user_0, addresses.DFX) / 1e18)
        print(i, user_1, euroc_usdc_gauge.claimable_reward(
            user_1, addresses.DFX) / 1e18)

        fastforward_chain(WEEK)

    distributor.distributeRewardToMultipleGauges(
        three_liquidity_gauges_v4, {'from': master_account, 'gas_price': gas_strategy})
    print(user_0, euroc_usdc_gauge.claimable_reward(
        user_0, addresses.DFX) / 1e18)
    print(user_1, euroc_usdc_gauge.claimable_reward(
        user_1, addresses.DFX) / 1e18)
    print(accounts[9], euroc_usdc_gauge.claimable_reward(
        accounts[9], addresses.DFX) / 1e18)

    fastforward_chain(WEEK * 210)
