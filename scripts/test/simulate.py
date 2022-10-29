#!/usr/bin/env python
"""
To simulate:
    1. Mint CADC/USDC tokens to default hardhat wallet
    2. Run this script
"""
from datetime import datetime

from brownie import chain

from scripts import contracts
from scripts.helper import get_addresses
from utils.constants import DFX_PRICE, TOKENLESS_PRODUCTION

addresses = get_addresses()

TEST_ADDR = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"  # any user address
DAY = 24 * 60 * 60
GAUGE_IDX = 0  # CADC/USDC
DFX_PRICE = 0.394651
LPT_PRICE = 0.9914504386743233


def get_gauge_lpt_balances(gauge, addr):
    lpt_addr = gauge.staking_token()
    lpt = contracts.dfx_curve(lpt_addr)
    lpt_user = gauge.balanceOf(addr)
    lpt_user_working = gauge.working_balances(addr)
    lpt_total = lpt.balanceOf(gauge)
    lpt_total_working = gauge.working_supply()
    lpt_pct = lpt_user / lpt_total * 100
    return lpt_user, lpt_user_working, lpt_total, lpt_total_working, lpt_pct


def get_vedfx_balances(addr):
    vedfx = contracts.voting_escrow(addresses.VOTE_ESCROW)
    vedfx_user = vedfx.balanceOf(addr)
    vedfx_total = vedfx.totalSupply()
    vedfx_pct = vedfx_user / vedfx_total * 100
    dfx_user_locked, dfx_user_expiration = vedfx.locked(addr)
    return dfx_user_locked, dfx_user_expiration, vedfx_user, vedfx_total, vedfx_pct


def get_available_rewards(gauge):
    _, _, _, rate, _, _ = gauge.reward_data(addresses.DFX)
    return rate * DAY * 7


def calc_earning_weight(lpt_user, lpt_total, vedfx_user, vedfx_total):
    lim = lpt_user * TOKENLESS_PRODUCTION / 100
    if vedfx_total > 0:
        lim += lpt_total * vedfx_user / vedfx_total * (100 - TOKENLESS_PRODUCTION) / 100
    return min(lpt_user, lim)


def get_user_apr(gauge, lpt_user, lpt_total, dfx_price, lpt_price):
    earning_weight = lpt_user
    available_rewards = get_available_rewards(gauge)
    boosted_rewards_weight = earning_weight / lpt_total
    boosted_rewards = boosted_rewards_weight * available_rewards
    yearly_rewards = boosted_rewards * 365 / 7
    return yearly_rewards, (yearly_rewards * dfx_price) / (lpt_user * lpt_price)


def main():
    gauge = contracts.gauges()[GAUGE_IDX]

    chain.sleep(0)
    chain_dt = datetime.fromtimestamp(chain.time())
    (
        user_lpt,
        user_lpt_working,
        total_lpt,
        total_lpt_working,
        lpt_pct,
    ) = get_gauge_lpt_balances(gauge, TEST_ADDR)
    (
        user_locked_dfx,
        user_lock_expires,
        user_vedfx,
        total_vedfx,
        vedfx_pct,
    ) = get_vedfx_balances(TEST_ADDR)
    yearly_rewards, apr = get_user_apr(
        gauge,
        user_lpt_working,
        total_lpt_working,
        DFX_PRICE,
        LPT_PRICE,
    )

    print(f"Chain time: {chain_dt}")
    print(f"LPT in Gauge: {user_lpt / 1e18} (total: {total_lpt / 1e18})")
    print(f"LPT %: {lpt_pct:.4f}%")
    print(f"User veDFX: {user_vedfx / 1e18} (total veDFX: {total_vedfx / 1e18})")
    print(f"veDFX %: {vedfx_pct:.4f}%")
    print(
        f"User locked DFX: {user_locked_dfx / 1e18} (expires {datetime.fromtimestamp(user_lock_expires)})"
    )
    print(f"APR: {apr*100}%")
    print(
        f"Yearly rewards: {yearly_rewards/1e18} / Daily rewards: {yearly_rewards/365/1e18}"
    )


if __name__ == "_main__":
    main()
