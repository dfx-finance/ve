#!/usr/bin/env python
from brownie import chain
import math
import pytest

from utils.apr import mint_lp_tokens
from utils.chain import (
    fastforward_chain,
    fastforward_chain_weeks,
    # fastforward_chain_anvil as fastforward_chain,
    # fastforward_chain_weeks_anvil as fastforward_chain_weeks,
)
from utils.gauges import deposit_lp_tokens, setup_distributor, setup_gauge_controller
from utils.gas import gas_strategy
from utils.helper import fund_multisigs, mint_dfx
from utils.ve import deposit_to_ve, submit_ve_vote
from .constants import EMISSION_RATE, TOTAL_DFX_REWARDS


# handle setup logic required for each unit test
@pytest.fixture(scope="function", autouse=True)
def setup(
    DFX,
    gauge_controller,
    three_gauges,
    distributor,
    deploy_account,
    multisig_0,
):
    fund_multisigs(deploy_account, [multisig_0])

    # setup gauges and distributor
    setup_gauge_controller(gauge_controller, three_gauges, multisig_0)

    # Params:
    # - reward token
    # - distributor contract
    # - account from which to mint and provide rewards to distributor contract
    # - account which administers the distributor contract
    # - rate dependent on tokens available and weekly reduction (see spreadsheet)
    setup_distributor(
        DFX,
        distributor,
        deploy_account,
        multisig_0,
        EMISSION_RATE,
        TOTAL_DFX_REWARDS,
    )


@pytest.fixture(scope="function", autouse=True)
def teardown():
    yield
    chain.reset()


##
## Tests
##
def test_single_user_unboosted(
    DFX,
    gauge_controller,
    distributor,
    three_lpts,
    three_gauges,
    deploy_account,
    multisig_0,
):
    fastforward_chain_weeks(num_weeks=0, delta=10)

    lpt, gauge = three_lpts[1], three_gauges[1]

    # deposit tokens to gauge
    deposit_lp_tokens(lpt, gauge, deploy_account)

    # artificially set gauge weight for our gauge
    gauge_controller.change_gauge_weight(
        gauge, 1 * 1e18, {"from": multisig_0, "gas_price": gas_strategy}
    )

    expected_rewards = [
        0,
        39696094673618000000000,
        79083866405146400000000,
        118165709965088000000000,
        156944001523560400000000,
    ]
    for i in range(5):
        fastforward_chain_weeks(num_weeks=0, delta=10)
        distributor.distributeRewardToMultipleGauges(
            three_gauges,
            {"from": multisig_0, "gas_price": gas_strategy},
        )

        assert math.isclose(
            gauge.claimable_reward(deploy_account, DFX),
            expected_rewards[i],
            rel_tol=1e-2,
        )


def test_single_user_claim(
    DFX,
    gauge_controller,
    distributor,
    three_lpts,
    three_gauges,
    deploy_account,
    multisig_0,
):
    test_single_user_unboosted(
        DFX,
        gauge_controller,
        distributor,
        three_lpts,
        three_gauges,
        deploy_account,
        multisig_0,
    )

    gauge = three_gauges[1]
    starting_dfx_balance = DFX.balanceOf(deploy_account)

    # claim staking reward
    reward_amount = gauge.claimable_reward(deploy_account, DFX)
    gauge.claim_rewards(
        deploy_account, {"from": deploy_account, "gas_price": gas_strategy}
    )
    # Test estimated and claimed rewards are similar to 0.1 DFX from raw 1e18 amount
    assert math.isclose(
        DFX.balanceOf(deploy_account) - starting_dfx_balance,
        reward_amount,
        rel_tol=1e-6,
    )


def test_multi_user_boosted(
    DFX,
    veDFX,
    gauge_controller,
    distributor,
    three_lpts,
    three_gauges,
    deploy_account,
    multisig_0,
    user_0,
    user_1,
):
    lpt, gauge = three_lpts[1], three_gauges[1]

    # Mint 10,000 of LP tokens are minted
    mint_lp_tokens(lpt, [user_0, user_1], deploy_account)

    # deposit tokens to gauge
    deposit_lp_tokens(lpt, gauge, user_0)
    deposit_lp_tokens(lpt, gauge, user_1)

    assert distributor.miningEpoch() == 0

    # (epoch 1) set chain to 10s before the week change and
    # distribute available reward to gauges
    fastforward_chain_weeks(num_weeks=1, delta=-10)
    distributor.distributeRewardToMultipleGauges(
        three_gauges, {"from": multisig_0, "gas_price": gas_strategy}
    )
    assert distributor.miningEpoch() == 1

    # (epoch 1) advance chain to 5h10s before next epoch change
    fastforward_chain_weeks(num_weeks=0, delta=-5 * 60 * 60 - 10)

    # mint 250,000 DFX
    mint_dfx(DFX, 2.5e23, user_0, deploy_account)

    # lock 1,000 DFX for 100 epochs
    lock_timestamp = chain.time()
    deposit_to_ve(DFX, veDFX, [user_0], [1e21], [100], lock_timestamp)

    # place votes in bps (10000 = 100.00%) for gauge 1
    submit_ve_vote(gauge_controller, three_gauges, [0, 10000, 0], user_0)

    # all voting power is registered on controller
    assert gauge_controller.vote_user_power(user_0) == 10000
    gauge.user_checkpoint(user_0, {"from": user_0, "gas_price": gas_strategy})

    # (epoch 1)
    fastforward_chain(int(chain.time()) + 4 * 60 * 60)

    # checkpoint necessary for calculating boost
    gauge.user_checkpoint(user_0, {"from": user_0, "gas_price": gas_strategy})
    assert int(gauge.claimable_reward(user_0, DFX) // 1e18) == 680
    assert distributor.miningEpoch() == 1

    # 10s before next epoch (2) begins
    fastforward_chain_weeks(num_weeks=0, delta=-10)

    # test next 5 epochs between naked and boosted rewards
    # 1. rewards are not claimed between rounds during test and therefore expected to accumulate
    # 2. expected rewards floored to nearest int value (whole DFX tokens) to allow for small variation between mining times
    expected = [
        # small difference for epoch 2 & 3 because ve deposit and voting hours before epoch change
        (2, 28576, 11430),
        (3, 28577, 11431),
        (4, 197328, 78931),
        (5, 280717, 112287),
        (6, 363455, 145382),
    ]

    for i in range(5):
        epoch, user0_rewards, user1_rewards = expected[i]

        distributor.distributeRewardToMultipleGauges(
            three_gauges,
            {"from": multisig_0, "gas_price": gas_strategy},
        )
        assert distributor.miningEpoch() == epoch

        # checkpoint for calculating boost
        gauge.user_checkpoint(user_0, {"from": user_0, "gas_price": gas_strategy})
        gauge.user_checkpoint(user_1, {"from": user_1, "gas_price": gas_strategy})

        assert int(gauge.claimable_reward(user_0, DFX) // 1e18) == user0_rewards
        assert int(gauge.claimable_reward(user_1, DFX) // 1e18) == user1_rewards

        fastforward_chain_weeks(num_weeks=0, delta=0)
