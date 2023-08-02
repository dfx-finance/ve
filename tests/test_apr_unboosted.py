#!/usr/bin/env python
from math import isclose
import pytest

import brownie
from brownie import accounts
from utils.apr import (
    distribute_to_gauges,
    calc_boosted_apr,
    claim_rewards,
    claimable_rewards,
    get_euroc_usdc_gauge,
    mint_lp_tokens,
)
from utils.chain import fastforward_chain_weeks
from utils.constants import EMISSION_RATE
from utils.gauges import deposit_lp_tokens, setup_distributor, setup_gauge_controller
from utils.gas import gas_strategy
from utils.network import get_network_addresses
from utils.helper import fund_multisigs

addresses = get_network_addresses()


# handle setup logic required for each unit test
@pytest.fixture(scope="module", autouse=True)
def setup(
    dfx,
    gauge_controller,
    three_liquidity_gauges_v4,
    distributor,
    master_account,
    new_master_account,
):
    fund_multisigs(master_account)

    # setup gauges and distributor
    setup_gauge_controller(gauge_controller, three_liquidity_gauges_v4, master_account)

    # Params:
    # - reward token
    # - distributor contract
    # - account from which to mint and provide rewards to distributor contract
    # - account which administers the distributor contract
    # - rate dependent on tokens available and weekly reduction (see spreadsheet)
    setup_distributor(
        dfx, distributor, master_account, new_master_account, EMISSION_RATE
    )


@pytest.fixture(scope="module", autouse=True)
def teardown():
    yield
    brownie.chain.reset()


def compare_available_rewards(dfx, gauge, users, expected_rewards, expected_sizes):
    available_rewards = claimable_rewards(dfx, gauge, users)

    # Compare user's share (as 0.0-1.0 ratio) of rewards
    for i, user in enumerate(users):
        expected_user_rewards = int(expected_rewards * expected_sizes[i])
        # Check w/in 99.99% of estimate
        assert isclose(available_rewards[user], expected_user_rewards, rel_tol=1e-4)

    return available_rewards


def compare_claimed_rewards(
    gauge, users, signer_account, expected_rewards, expected_sizes
):
    rewards = claim_rewards(gauge, addresses.DFX, users, signer_account)
    for i, user in enumerate(users):
        expected_user_rewards = int(expected_rewards * expected_sizes[i])
        # Check w/in 99.99% of estimate
        assert isclose(rewards[user], expected_user_rewards, rel_tol=1e-4)
    return rewards


def test_unboosted_apr(
    dfx,
    mock_lp_tokens,
    gauge_controller,
    distributor,
    voting_escrow,
    veboost_proxy,
    three_liquidity_gauges_v4,
    master_account,
):
    # two random users
    user_0 = accounts[4]
    user_1 = accounts[5]

    # select the EUROC/USDC LP token and gauge for depositing
    euroc_usdc_lp, euroc_usdc_gauge = get_euroc_usdc_gauge(
        mock_lp_tokens, three_liquidity_gauges_v4
    )

    # 1. Test that expected amount of LP tokens are minted
    mint_lp_tokens(euroc_usdc_lp, [user_0, user_1], master_account)

    # 2a. Test that epoch 0 is the current epoch
    # fast-forward to 5s after epoch 0 start
    fastforward_chain_weeks(num_weeks=1, delta=5)
    assert distributor.miningEpoch() == 0

    # 2b. Test that gauge distributions at beginning of epoch 0 results in the expected amount of rewards
    # at start of epoch 0.

    # update mining params for first week's distribution
    # NOTE: this will be called within distributor if this hasn't been called yet
    distributor.updateMiningParameters(
        {"from": master_account, "gas_price": gas_strategy}
    )

    week_rate = distributor.rate()
    week_seconds = 3600 * 24 * 7
    tx = gauge_controller.gauge_relative_weight_write(
        euroc_usdc_gauge,
        {"from": master_account, "gas_price": gas_strategy},
    )
    gauge_weight = tx.return_value
    expected_rewards = int((week_rate * gauge_weight * week_seconds) / 1e18)

    distribute_to_gauges(
        dfx,
        distributor,
        three_liquidity_gauges_v4,
        master_account,
        {euroc_usdc_gauge: expected_rewards},
    )
    assert distributor.miningEpoch() == 1

    # 2c. Deposit LP tokens into the gauge for epoch 0 rewards.
    deposit_lp_tokens(euroc_usdc_lp, euroc_usdc_gauge, user_0)
    deposit_lp_tokens(euroc_usdc_lp, euroc_usdc_gauge, user_1)

    # 3. Fast-forward until the very end of epoch 1 and claim rewards. Check available rewards, claimed rewards
    # and unboosted APR
    fastforward_chain_weeks(num_weeks=1, delta=-10)

    available_rewards = compare_available_rewards(
        dfx,
        euroc_usdc_gauge,
        [user_0, user_1],
        expected_rewards,
        expected_sizes=[0.5, 0.5],
    )
    compare_claimed_rewards(
        euroc_usdc_gauge,
        [user_0, user_1],
        master_account,
        expected_rewards,
        expected_sizes=[0.5, 0.5],
    )
    apr = calc_boosted_apr(
        voting_escrow,
        veboost_proxy,
        euroc_usdc_gauge,
        user_0,
        available_rewards["combined"],
    )
    assert isclose(apr, 8.23240494389279, abs_tol=1e-4)
