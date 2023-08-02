#!/usr/bin/env python
import brownie
from math import isclose
import pytest

from utils.chain import fastforward_chain_weeks
from utils.constants import EMISSION_RATE
from utils.gauges import deposit_lp_tokens, setup_distributor, setup_gauge_controller
from utils.gas import gas_strategy
from utils.network import get_network_addresses
from utils.helper import assert_tokens_balance, fund_multisigs, mint_dfx


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


def test_single_user_two_distributors(
    dfx,
    mock_lp_tokens,
    three_liquidity_gauges_v4,
    gauge_controller,
    distributor,
    master_account,
    new_master_account,
):
    # check that we have been pre-minted LP tokens
    assert_tokens_balance(mock_lp_tokens, master_account, 1e9)

    # select the EUROC LP token and gauge for depositing
    euroc_usdc_lp = mock_lp_tokens[1]
    euroc_usdc_gauge = three_liquidity_gauges_v4[1]
    assert "euroc" in euroc_usdc_lp.name().lower()
    assert "euroc" in euroc_usdc_gauge.name().lower()

    # deposit tokens to gauge
    deposit_lp_tokens(euroc_usdc_lp, euroc_usdc_gauge, master_account)

    # artificially set gauge weight for our gauge
    gauge_controller.change_gauge_weight(
        euroc_usdc_gauge, 1 * 1e18, {"from": master_account, "gas_price": gas_strategy}
    )

    # call rewards distribution in various epochs:
    # rewards = [Wednesday before epoch 0, epoch 1, epoch 2, ...]
    expected_rewards = [
        0,
        14999718292392400000000,
        69757690478819200000000,
        124206654953819200000000,
        178349215967749600000000,
    ]
    for i in range(5):
        distributor.distributeRewardToMultipleGauges(
            three_liquidity_gauges_v4,
            {"from": master_account, "gas_price": gas_strategy},
        )

        # Manually distribute rewards to gauge via the distributor contract
        mint_dfx(dfx, 15000 * 1e18, new_master_account)
        dfx.approve(
            distributor,
            15000 * 1e18,
            {"from": new_master_account, "gas_price": gas_strategy},
        )
        distributor.passRewardToGauge(
            euroc_usdc_gauge,
            addresses.DFX,
            15000 * 1e18,
            {"from": new_master_account, "gas_price": gas_strategy},
        )

        claimable_reward = euroc_usdc_gauge.claimable_reward(
            master_account, addresses.DFX
        )
        assert isclose(claimable_reward, expected_rewards[i], rel_tol=1e-4)

        fastforward_chain_weeks(num_weeks=1, delta=10)
