#!/usr/bin/env python
import brownie
from brownie import accounts
from math import isclose
import pytest

from fork.constants import EMISSION_RATE
from utils.apr import (
    calc_boosted_apr,
    claimable_rewards,
    distribute_to_gauges,
    get_euroc_usdc_gauge,
    mint_lp_tokens,
    mint_vedfx_and_vote,
)
from utils.chain import fastforward_chain_weeks
from utils.helper import fund_multisigs
from utils.gauges import deposit_lp_tokens, setup_distributor, setup_gauge_controller


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


def test_boosted_apr(
    dfx,
    mock_lp_tokens,
    distributor,
    gauge_controller,
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

    fastforward_chain_weeks(num_weeks=1, delta=5)

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
    deposit_lp_tokens(euroc_usdc_lp, euroc_usdc_gauge, user_1)

    # 2d. Lock DFX for veDFX for user0 and vote for gauge
    mint_vedfx_and_vote(
        dfx,
        gauge_controller,
        voting_escrow,
        three_liquidity_gauges_v4,
        euroc_usdc_gauge,
        user_0,
    )

    print(user_0)

    # 3. Fast-forward until the very end of epoch 1 and claim rewards. Check theoretical vs
    # actually claimed rewards and calculated unboosted APR
    fastforward_chain_weeks(num_weeks=1, delta=-10)

    users = [user_0, user_1]
    available_rewards = claimable_rewards(dfx, euroc_usdc_gauge, users)

    expected = [20.581012359731975, 8.23240494389279]
    for i, user in enumerate(users):
        apr = calc_boosted_apr(
            voting_escrow,
            veboost_proxy,
            euroc_usdc_gauge,
            user,
            available_rewards["combined"],
        )
        assert isclose(apr, expected[i], rel_tol=1e-4)
