#!/usr/bin/env python
from .chain import gas_strategy
from .token import mint_dfx, send_dfx
from .constants import (
    DEFAULT_GAUGE_TYPE,
    DEFAULT_GAUGE_WEIGHT,
    DEFAULT_TYPE_WEIGHT,
    TOTAL_DFX_REWARDS
)


def setup_gauge_controller(gauge_controller, gauges, master_account):
    gauge_controller.add_type(
        'AMM Liquidity Pools', DEFAULT_TYPE_WEIGHT, {'from': master_account, 'gas_price': gas_strategy})
    for gauge in gauges:
        gauge_controller.add_gauge(
            gauge, DEFAULT_GAUGE_TYPE, DEFAULT_GAUGE_WEIGHT, {'from': master_account, 'gas_price': gas_strategy})


def setup_distributor(dfx, distributor, master_account, new_master_account, rate):
    # Supply master account contract with rewards
    mint_dfx(dfx, TOTAL_DFX_REWARDS, master_account)

    # Distribute rewards to the distributor contract
    send_dfx(dfx, TOTAL_DFX_REWARDS, master_account, distributor)

    # Set rate to distribute 1,000,000 rewards (see spreadsheet)
    distributor.setRate(
        rate, {'from': new_master_account, 'gas_price': gas_strategy})

    # Turn on distributions to gauges
    distributor.toggleDistributions(
        {'from': new_master_account, 'gas_price': gas_strategy})


def deposit_lp_tokens(lp_token, gauge, account):
    # deposit LP token into gauge
    amount = lp_token.balanceOf(account)
    lp_token.approve(gauge, amount, {
        'from': account, 'gas_price': gas_strategy})
    gauge.deposit(
        amount, {'from': account, 'gas_price': gas_strategy})

    # check that LP has been transfered
    assert lp_token.balanceOf(account) == 0
