#!/usr/bin/env python
import brownie
import pytest

import addresses
from utils import fastforward_chain, fund_multisig, assert_tokens_balance, gas_strategy
from utils_gauges import deposit_lp_tokens, setup_distributor, setup_gauge_controller
from utils_ve import EMISSION_RATE, WEEK


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


def test_single_user_stake(dfx, mock_lp_tokens, three_liquidity_gauges_v4, gauge_controller, distributor, master_account):
    starting_dfx_balance = dfx.balanceOf(master_account)

    # check that we have been pre-minted LP tokens
    assert_tokens_balance(mock_lp_tokens, master_account, 1e9)

    # select the EUROC LP token and gauge for depositing
    euroc_usdc_lp = mock_lp_tokens[1]
    euroc_usdc_gauge = three_liquidity_gauges_v4[1]
    assert 'euroc' in euroc_usdc_lp.name().lower()
    assert 'euroc' in euroc_usdc_gauge.name().lower()

    # deposit tokens to gauge
    deposit_lp_tokens(euroc_usdc_lp, euroc_usdc_gauge, master_account)

    # artificially set gauge weight for our gauge
    gauge_controller.change_gauge_weight(
        euroc_usdc_gauge, 1 * 1e18, {'from': master_account, 'gas_price': gas_strategy})

    # call rewards distribution in various epochs:
    # rewards = [Wednesday before epoch 0, epoch 1, epoch 2, ...]
    expected_rewards = [0, 0, 3207448777992800000000,
                        6389985028646000000000, 9547802249677200000000]
    for i in range(5):
        distributor.distributeRewardToMultipleGauges(
            three_liquidity_gauges_v4, {'from': master_account, 'gas_price': gas_strategy})

        assert euroc_usdc_gauge.claimable_reward(
            master_account, addresses.DFX) == expected_rewards[i]

        fastforward_chain(WEEK)

    # claim staking reward
    reward_amount = euroc_usdc_gauge.claimable_reward(
        master_account, addresses.DFX)
    euroc_usdc_gauge.claim_rewards(
        master_account, {'from': master_account, 'gas_price': gas_strategy})
    assert (dfx.balanceOf(master_account) -
            starting_dfx_balance) == reward_amount
