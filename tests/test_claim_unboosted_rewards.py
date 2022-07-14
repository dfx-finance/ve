#!/usr/bin/env python
from brownie.network.gas.strategies import LinearScalingStrategy
import pytest

import addresses
import utils


TOTAL_DFX_REWARDS = 1_000_000 * 1e18

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('30 gwei', '250 gwei', 1.3)


# handle setup logic required for each unit test
@pytest.fixture(scope='module', autouse=True)
def setup(dfx, gauge_controller, three_liquidity_gauges_v4, distributor, master_account, new_master_account):
    utils.fund_multisig(master_account)
    utils.setup_gauge_controller(
        gauge_controller, three_liquidity_gauges_v4, master_account)

    # Supply distributor contract with rewards
    utils.mint_dfx(dfx, TOTAL_DFX_REWARDS, master_account)

    # Distribute rewards to the distributor contract
    utils.send_dfx(dfx, TOTAL_DFX_REWARDS, master_account, distributor)

    # Turn on distributions to gauges
    distributor.toggleDistributions(
        {'from': new_master_account, 'gas_price': gas_strategy})

    # Set rate to distribute 1,000,000 rewards (see spreadsheet)
    distributor.setRate(
        1.2842402e16, {'from': new_master_account, 'gas_price': gas_strategy})


def deposit_lp_tokens(lp_token, gauge, account):
    # deposit LP token into gauge
    amount = lp_token.balanceOf(account)
    lp_token.approve(gauge, amount, {
        'from': account, 'gas_price': gas_strategy})
    gauge.deposit(
        amount, {'from': account, 'gas_price': gas_strategy})

    # check that LP has been transfered
    assert lp_token.balanceOf(account) == 0
    assert lp_token.balanceOf(gauge) == amount


def test_single_user_stake(dfx, mock_lp_tokens, three_liquidity_gauges_v4, gauge_controller, distributor, master_account):
    starting_dfx_balance = dfx.balanceOf(master_account)

    # check that we have been pre-minted LP tokens
    for lp_token in mock_lp_tokens:
        balance = lp_token.balanceOf(master_account)
        print(f'{lp_token.name()}: {balance/1e18}')

    # select the EURS LP token and gauge for depositing
    eurs_usdc_lp = mock_lp_tokens[1]
    eurs_usdc_gauge = three_liquidity_gauges_v4[1]
    assert 'eurs' in eurs_usdc_lp.name().lower()
    assert 'eurs' in eurs_usdc_gauge.name().lower()

    # deposit tokens to gauge
    deposit_lp_tokens(eurs_usdc_lp, eurs_usdc_gauge, master_account)

    # artificially set gauge weight for our gauge
    gauge_controller.change_gauge_weight(
        eurs_usdc_gauge, 1 * 1e18, {'from': master_account, 'gas_price': gas_strategy})

    # call rewards distribution in various epochs:
    # rewards = [Wednesday before epoch 0, Epoch 0, Epoch 1, ...]
    expected_rewards = [0, 0, 7706757122187200000000,
                        15353655206616800000000, 22941159183524400000000]
    for i in range(5):
        distributor.distributeRewardToMultipleGauges(
            three_liquidity_gauges_v4, {'from': master_account, 'gas_price': gas_strategy})

        assert eurs_usdc_gauge.claimable_reward(
            master_account, addresses.DFX) == expected_rewards[i]

        utils.fastforward_chain(utils.WEEK)

    # claim staking reward
    reward_amount = eurs_usdc_gauge.claimable_reward(
        master_account, addresses.DFX)
    eurs_usdc_gauge.claim_rewards(
        master_account, {'from': master_account, 'gas_price': gas_strategy})
    assert (dfx.balanceOf(master_account) -
            starting_dfx_balance) == reward_amount
