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
from utils.constants import WEEK
from utils.helper import mint_dfx
from utils.gauges import deposit_lp_tokens
from utils.ve import deposit_to_ve, submit_ve_vote

from utils.gauges import setup_distributor, setup_gauge_controller

from utils.gas import gas_strategy
from utils.helper import fund_multisigs
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


def test_delegate(
    DFX,
    veDFX,
    gauge_controller,
    distributor,
    boostV2,
    veboost_proxy,
    three_lpts,
    three_gauges,
    deploy_account,
    multisig_0,
    multisig_1,
    user_0,
    user_1,
):
    lpt, gauge = three_lpts[1], three_gauges[1]

    # Set delegation contract on veboost proxy
    veboost_proxy.set_delegation(
        boostV2, {"from": multisig_0, "gas_price": gas_strategy}
    )

    # Setup voting protocol
    mint_dfx(DFX, 1e18, user_1, deploy_account)
    lock_timestamp = chain.time()
    deposit_to_ve(DFX, veDFX, [user_1], [1e18], [200], lock_timestamp)

    # Setup user to delegate votes to protocol
    mint_dfx(DFX, 2.5e23, user_0, deploy_account)
    lock_timestamp = chain.time()
    deposit_to_ve(DFX, veDFX, [user_0], [1e21], [100], lock_timestamp)
    mint_lp_tokens(three_lpts[0], [user_0], deploy_account)
    deposit_lp_tokens(three_lpts[0], three_gauges[0], user_0)
    mint_lp_tokens(three_lpts[1], [user_0], deploy_account)
    deposit_lp_tokens(three_lpts[1], three_gauges[1], user_0)

    assert distributor.miningEpoch() == 0
    assert math.isclose(
        veboost_proxy.adjusted_balance_of(user_0), 479452054794511680000, rel_tol=1e-4
    )  # ~479.45 veDFX
    assert math.isclose(
        veboost_proxy.adjusted_balance_of(user_1), 958904101547752005, rel_tol=1e-4
    )  # ~0.95 veDFX

    # Seed gauges with 1 week rewards
    fastforward_chain_weeks(num_weeks=1, delta=-10)
    distributor.distributeRewardToMultipleGauges(
        three_gauges, {"from": multisig_0, "gas_price": gas_strategy}
    )
    assert distributor.miningEpoch() == 1

    # Delegate from user to the protocol for 25 weeks
    del_bal = boostV2.delegable_balance(user_0)
    expiration = (lock_timestamp + 25 * WEEK) // WEEK * WEEK
    boostV2.boost(
        user_1, del_bal, expiration, {"from": user_0, "gas_price": gas_strategy}
    )
    assert math.isclose(
        veboost_proxy.adjusted_balance_of(user_1), 470812408120744300290, rel_tol=1e-4
    )  # ~470.81 veDFX

    # Vote on behalf of user
    # place votes in bps (10000 = 100.00%) for gauge 1
    submit_ve_vote(gauge_controller, three_gauges, [0, 10000, 0], user_1)
    assert gauge_controller.vote_user_power(user_1) == 10000

    # Distribute available reward to gauges
    fastforward_chain_weeks(num_weeks=1, delta=10)
    distributor.distributeRewardToMultipleGauges(
        three_gauges, {"from": multisig_0, "gas_price": gas_strategy}
    )
    assert distributor.miningEpoch() == 3

    # Check rewards are claimable by original user and that boosted rewards
    # are greater than unboosted rewards
    fastforward_chain(int(chain.time()) + 12 * 60 * 60)
    user0_gauge0_rewards = three_gauges[0].claimable_reward(user_0, DFX)
    user0_gauge1_rewards = three_gauges[1].claimable_reward(user_0, DFX)
    user1_gauge0_rewards = three_gauges[0].claimable_reward(user_1, DFX)
    user1_gauge1_rewards = three_gauges[1].claimable_reward(user_1, DFX)
    assert math.isclose(user0_gauge0_rewards, 44300436864029359426935, rel_tol=1e-4)
    assert math.isclose(user0_gauge1_rewards, 48366162469641074567609, rel_tol=1e-4)
    assert user1_gauge0_rewards == 0
    assert user1_gauge1_rewards == 0
