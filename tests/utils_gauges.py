#!/usr/bin/env python
from brownie.network.gas.strategies import LinearScalingStrategy

from utils import mint_dfx, send_dfx

DEFAULT_GAUGE_TYPE = 0  # Ethereum stableswap pools
DEFAULT_TYPE_WEIGHT = 1e18
DEFAULT_GAUGE_WEIGHT = 0

TOTAL_DFX_REWARDS = 1_000_000 * 1e18


# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('30 gwei', '250 gwei', 1.3)


def setup_gauge_controller(gauge_controller, gauges, master_account):
    gauge_controller.add_type(
        'AMM Liquidity Pools', DEFAULT_TYPE_WEIGHT, {'from': master_account, 'gas_price': gas_strategy})
    for gauge in gauges:
        gauge_controller.add_gauge(
            gauge, DEFAULT_GAUGE_TYPE, DEFAULT_GAUGE_WEIGHT, {'from': master_account, 'gas_price': gas_strategy})


def setup_distributor(dfx, distributor, master_account, new_master_account, rate):
    # Supply distributor contract with rewards
    mint_dfx(dfx, TOTAL_DFX_REWARDS, master_account)

    # Distribute rewards to the distributor contract
    send_dfx(dfx, TOTAL_DFX_REWARDS, master_account, distributor)

    # Turn on distributions to gauges
    distributor.toggleDistributions(
        {'from': new_master_account, 'gas_price': gas_strategy})

    # Set rate to distribute 1,000,000 rewards (see spreadsheet)
    distributor.setRate(
        rate, {'from': new_master_account, 'gas_price': gas_strategy})


def deposit_lp_tokens(lp_token, gauge, account):
    # deposit LP token into gauge
    amount = lp_token.balanceOf(account)
    lp_token.approve(gauge, amount, {
        'from': account, 'gas_price': gas_strategy})
    gauge.deposit(
        amount, {'from': account, 'gas_price': gas_strategy})

    # check that LP has been transfered
    assert lp_token.balanceOf(account) == 0
