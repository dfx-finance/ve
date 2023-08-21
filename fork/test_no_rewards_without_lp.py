#!/usr/bin/env python
import brownie
from brownie import accounts
import math
import pytest

from fork.constants import EMISSION_RATE
from utils.apr import (
    calc_theoretical_rewards,
    claim_rewards,
    claimable_rewards,
    distribute_to_gauges,
    gauge_relative_weights,
    get_euroc_usdc_gauge,
    mint_lp_tokens,
)
from utils.chain import fastforward_chain_weeks
from utils.gauges import deposit_lp_tokens, setup_distributor, setup_gauge_controller
from utils.gas import gas_strategy
from utils.helper import fund_multisigs, mint_dfx
from utils.network import get_network_addresses
from utils.ve import deposit_to_ve, submit_ve_vote

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


def test_only_lp_rewarded(
    dfx,
    mock_lp_tokens,
    voting_escrow,
    gauge_controller,
    distributor,
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
    mint_lp_tokens(euroc_usdc_lp, [user_0], master_account)

    # 2a. Test that epoch 0 is the current epoch
    # fast-forward to 5s after epoch 0 start
    fastforward_chain_weeks(num_weeks=1, delta=5)
    assert distributor.miningEpoch() == 0

    # 2b. Test that gauge distributions at beginning of epoch 0 results in the expected amount of rewards
    # at start of epoch 0.
    distribute_to_gauges(
        dfx,
        distributor,
        three_liquidity_gauges_v4,
        master_account,
        {euroc_usdc_gauge: 39757766414611472197042},
    )
    assert distributor.miningEpoch() == 1

    # 2c. Deposit LP tokens into the gauge for epoch 0 rewards.
    deposit_lp_tokens(euroc_usdc_lp, euroc_usdc_gauge, user_0)
    # 2d. Lock DFX for veDFX for user0 and vote for gauge
    mint_dfx(dfx, 5e24, user_0)
    mint_dfx(dfx, 5e24, user_1)
    lock_timestamp = brownie.chain.time()
    deposit_to_ve(
        dfx, voting_escrow, [user_0, user_1], [1e21, 1e24], [100, 208], lock_timestamp
    )
    # Place votes in bps (10000 = 100.00%)
    submit_ve_vote(gauge_controller, three_liquidity_gauges_v4, [0, 10000, 0], user_0)
    submit_ve_vote(gauge_controller, three_liquidity_gauges_v4, [0, 10000, 0], user_1)
    assert gauge_controller.vote_user_power(user_0) == 10000
    assert gauge_controller.vote_user_power(user_1) == 10000
    euroc_usdc_gauge.user_checkpoint(
        user_0, {"from": user_0, "gas_price": gas_strategy}
    )

    # 3. Fast-forward until the very end of epoch 1 and claim rewards. Check that only
    # first user with deposited LP rewards despite both users holding veDFX and voting
    fastforward_chain_weeks(num_weeks=1, delta=-10)

    users = [user_0, user_1]
    available_rewards = claimable_rewards(dfx, euroc_usdc_gauge, users)
    rewards = claim_rewards(euroc_usdc_gauge, addresses.DFX, users, master_account)

    # 4. Calculate theoretical rewards to be received vs actually available and claimed by user
    gauge_weights = gauge_relative_weights(gauge_controller, three_liquidity_gauges_v4)
    _, expected_gauge_rewards = calc_theoretical_rewards(
        distributor, gauge_weights[euroc_usdc_gauge]
    )
    expected_available = [expected_gauge_rewards, 0]
    expected_claimed = [expected_gauge_rewards, 0]
    for i, user in enumerate(users):
        assert math.isclose(
            available_rewards[user], expected_available[i], rel_tol=1e-4
        )
        assert math.isclose(rewards[user], expected_claimed[i], rel_tol=1e-4)