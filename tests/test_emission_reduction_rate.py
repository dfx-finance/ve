#!/usr/bin/env python
from brownie import accounts, chain
import pytest

import addresses
from utils import fastforward_chain, fund_multisig, mint_dfx, gas_strategy
from utils_gauges import deposit_lp_tokens, setup_distributor, setup_gauge_controller, TOTAL_DFX_REWARDS
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
def teardown(dfx, voting_escrow):
    yield

    # same two users
    user_account = accounts[4]

    # Withdraw all tokens from lock
    print(f'Withdrawing {user_account}...')
    voting_escrow.withdraw({'from': user_account, 'gas_price': gas_strategy})

    # Burn DFX user balance
    burn_amt = dfx.balanceOf(user_account)
    dfx.transfer(addresses.DFX_MULTISIG, burn_amt, {
                 'from': user_account, 'gas_price': gas_strategy})


def test_full_distribution(dfx, mock_lp_tokens, voting_escrow, three_liquidity_gauges_v4, gauge_controller, distributor, master_account):
    # some ordinary user
    user_account = accounts[4]

    # select the EUROC LP token and gauge for depositing
    euroc_usdc_lp = mock_lp_tokens[1]
    euroc_usdc_gauge = three_liquidity_gauges_v4[1]
    assert 'euroc' in euroc_usdc_lp.name().lower()
    assert 'euroc' in euroc_usdc_gauge.name().lower()

    # mint 10,000 lp tokens for the users
    lp_amount = 10e21
    euroc_usdc_lp.mint(user_account, lp_amount, {
        'from': master_account, 'gas_price': gas_strategy})
    assert euroc_usdc_lp.balanceOf(user_account) == lp_amount

    # deposit tokens to gauge
    deposit_lp_tokens(euroc_usdc_lp, euroc_usdc_gauge, user_account)

    # for user, mint 250,000 dfx and lock it for 4 years
    dfx_amount = 2.5e23
    mint_dfx(dfx, dfx_amount, user_account)
    assert dfx.balanceOf(user_account) == dfx_amount

    # Init 10 s before the week change
    t0 = chain.time()
    timestamp = (t0 + WEEK) // WEEK * WEEK - 10
    deposit_to_ve(dfx, voting_escrow, [user_account], [
                  2.5e23], [208], timestamp)

    submit_ve_vote(gauge_controller, three_liquidity_gauges_v4,
                   [0, 10000, 0], user_account)

    print("Emission start time:", distributor.startEpochTime())

    total_distributed = 0
    for i in range(208):
        print()
        print("Epoch start time:", distributor.startEpochTime())
        print("Round start distributed:",
              distributor.startEpochSupply() / 1e18)

        distributor.distributeRewardToMultipleGauges(
            three_liquidity_gauges_v4, {'from': master_account, 'gas_price': gas_strategy})

        distributor_balance = dfx.balanceOf(distributor)
        distributed_amount = (TOTAL_DFX_REWARDS -
                              distributor_balance) - total_distributed

        print(
            f'Epoch {i} - Remaining balance: {distributor_balance} Epoch distribution: {distributed_amount / 1e18}')

        total_distributed += distributed_amount
        fastforward_chain(WEEK)
