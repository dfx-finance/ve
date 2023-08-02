#!/usr/bin/env python
import brownie
from datetime import datetime
import math

from .bignum import approximately_equals
from .chain import gas_strategy
from .constants import WEEK, EPOCHS_PER_YEAR, TOKENLESS_PRODUCTION, DFX_PRICE, LP_PRICE
from .testing.token import mint_dfx
from .ve import deposit_to_ve, submit_ve_vote


# Print current chain time and epoch
def log_times(distributor, stage):
    now = brownie.chain.time()
    print(f"{stage} -- chain time:", datetime.fromtimestamp(now))
    print(f"{stage} -- current epoch:", distributor.miningEpoch())


def get_cadc_usdc_gauge(mock_lp_tokens, three_liquidity_gauges_v4):
    cadc_usdc_lp = mock_lp_tokens[0]
    cadc_usdc_gauge = three_liquidity_gauges_v4[0]
    assert "cadc" in cadc_usdc_lp.name().lower()
    assert "cadc" in cadc_usdc_gauge.name().lower()
    return cadc_usdc_lp, cadc_usdc_gauge


def get_euroc_usdc_gauge(mock_lp_tokens, three_liquidity_gauges_v4):
    euroc_usdc_lp = mock_lp_tokens[1]
    euroc_usdc_gauge = three_liquidity_gauges_v4[1]
    assert "euroc" in euroc_usdc_lp.name().lower()
    assert "euroc" in euroc_usdc_gauge.name().lower()
    return euroc_usdc_lp, euroc_usdc_gauge


# mint lp tokens for the users (default: 10,000)
def mint_lp_tokens(euroc_usdc_lp, users, signer_account, amount=10e21):
    for user in users:
        euroc_usdc_lp.mint(
            user, amount, {"from": signer_account, "gas_price": gas_strategy}
        )
        assert euroc_usdc_lp.balanceOf(user) == amount


def mint_vedfx_and_vote(
    dfx,
    gauge_controller,
    voting_escrow,
    three_liquidity_gauges_v4,
    voted_gauge,
    account,
    amount=1e5,
):
    mint_dfx(dfx, amount * 1e18, account)
    lock_timestamp = brownie.chain.time()
    deposit_to_ve(dfx, voting_escrow, [account], [1e21], [100], lock_timestamp)
    # Place votes in bps (10000 = 100.00%)
    submit_ve_vote(gauge_controller, three_liquidity_gauges_v4, [0, 10000, 0], account)
    assert gauge_controller.vote_user_power(account) == 10000
    voted_gauge.user_checkpoint(account, {"from": account, "gas_price": gas_strategy})


# Distribute rewards to all registered gauges and return balances
def distribute_to_gauges(dfx, distributor, gauges, account, assertions):
    distributor.distributeRewardToMultipleGauges(
        gauges, {"from": account, "gas_price": gas_strategy}
    )
    balances = {g: dfx.balanceOf(g) for g in gauges}
    for g, expected_balance in assertions.items():
        # approximate deviation between calling updateMiningParameters
        print(expected_balance, balances[g])
        assert math.isclose(
            expected_balance,
            balances[g],
            rel_tol=1e-4,
        )
    return balances


# Fetch relative weights of all registered gauges
def gauge_relative_weights(gauge_controller, gauges):
    weights = {}
    for g in gauges:
        weights[g] = gauge_controller.gauge_relative_weight(g)
    return weights


# Fetch the available rewards to claim for all users
def claimable_rewards(dfx, gauge, users):
    rewards = {}
    total = 0
    for u in users:
        amount = gauge.claimable_reward(u, dfx.address)
        rewards[u] = amount
        total += amount
    rewards["combined"] = dfx.balanceOf(gauge)
    return rewards


def claim_rewards(gauge, reward_address, users, signer_account):
    rewards = {}
    total = 0
    for u in users:
        gauge.claim_rewards(u, {"from": signer_account, "gas_price": gas_strategy})
        amount = gauge.claimed_reward(u, reward_address)
        rewards[u] = amount
        total += amount
    rewards["combined"] = total
    return rewards


def calc_theoretical_rewards(distributor, gauge_weight):
    global_rewards = distributor.rate() * WEEK
    gauge_rewards = global_rewards * gauge_weight / 1e18
    return global_rewards, gauge_rewards


def calc_theoretical_rewards_full(
    distributor, gauge_controller, gauge, weeks_elapsed, signer_account
):
    week_rate = distributor.rate()
    rate_reduction = distributor.RATE_REDUCTION_COEFFICIENT()
    rewards = 0
    week_seconds = 3600 * 24 * 7
    for i in range(weeks_elapsed):
        if i == 0:
            tx = gauge_controller.gauge_relative_weight_write(
                gauge,
                brownie.chain.time(),
                {"from": signer_account, "gas_price": gas_strategy},
            )
            gauge_weight = tx.return_value
        else:
            gauge_weight = gauge_controller.gauge_relative_weight(
                gauge, brownie.chain.time() - week_seconds * i
            )

        rewards += (week_rate * gauge_weight * week_seconds) / 1e18
        week_rate = week_rate * rate_reduction / 1e18
    return rewards


# boosted_weight = (gauge_lp_balance * 40/100) + \
#     (gauge_lp_total * voting_balance / voting_total * (100-40)/100)
def calc_earning_weight(lp_balance, lp_total, voting_balance, voting_total):
    lim = lp_balance * TOKENLESS_PRODUCTION / 100
    if voting_total > 0:
        lim += (
            lp_total
            * voting_balance
            / voting_total
            * (100 - TOKENLESS_PRODUCTION)
            / 100
        )
    return min(lp_balance, lim)


# https://resources.curve.fi/reward-gauges/boosting-your-crv-rewards
# https://gov.balanced.network/t/baln-token-economics-enhancement-bbaln/161
def calc_boosted_apr(voting_escrow, veboost_proxy, gauge, account, available_rewards):
    gauge_lp_balance = gauge.balanceOf(account)
    gauge_lp_total = gauge.totalSupply()
    voting_balance = veboost_proxy.adjusted_balance_of(account)
    voting_total = voting_escrow.totalSupply()

    earning_weight = calc_earning_weight(
        gauge_lp_balance, gauge_lp_total, voting_balance, voting_total
    )

    boosted_rewards_weight = earning_weight / gauge_lp_total
    boosted_rewards = boosted_rewards_weight * available_rewards
    yearly_rewards = boosted_rewards * EPOCHS_PER_YEAR
    if gauge_lp_balance:
        return (yearly_rewards * DFX_PRICE) / (gauge_lp_balance * LP_PRICE)
    return 0


def calc_global_boosted_apr(gauge, available_rewards):
    gauge_lp_total = gauge.totalSupply()
    yearly_rewards = available_rewards * EPOCHS_PER_YEAR
    if gauge_lp_total:
        return (yearly_rewards * DFX_PRICE) / (gauge_lp_total * LP_PRICE)
    return 0


# boosted_weight = (gauge_lp_balance * 40/100) + \
#     (gauge_lp_total * voting_balance / voting_total * (100-40)/100)
def calc_required_vedfx(voting_escrow, veboost_proxy, gauge, account):
    gauge_lp_balance = gauge.balanceOf(account)
    gauge_lp_total = gauge.totalSupply()
    voting_balance = veboost_proxy.adjusted_balance_of(account)
    voting_total = voting_escrow.totalSupply()

    earning_weight = calc_earning_weight(
        gauge_lp_balance, gauge_lp_total, voting_balance, voting_total
    )

    additional_vedfx = 0
    while True:
        if earning_weight < gauge_lp_balance:
            a = gauge_lp_balance - (gauge_lp_balance * TOKENLESS_PRODUCTION / 100)
            b = (a / (100 - TOKENLESS_PRODUCTION) / 100) / voting_total * gauge_lp_total
            additional_vedfx += b
            voting_balance += b
            voting_total += b
            earning_weight = calc_earning_weight(
                gauge_lp_balance, gauge_lp_total, voting_balance, voting_total
            )
        else:
            break
    return additional_vedfx
