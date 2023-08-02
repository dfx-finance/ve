#!/usr/bin/env python
from .constants import (
    DEFAULT_TYPE_WEIGHT,
    DEFAULT_GAUGE_TYPE,
    DEFAULT_GAUGE_WEIGHT,
    TOTAL_DFX_REWARDS,
)
from .gas import gas_strategy
from .helper import mint_dfx, send_dfx


def setup_gauge_controller(gauge_controller, gauges, master_account):
    gauge_controller.add_type(
        "AMM Liquidity Pools",
        DEFAULT_TYPE_WEIGHT,
        {"from": master_account, "gas_price": gas_strategy},
    )
    for gauge in gauges:
        gauge_controller.add_gauge(
            gauge,
            DEFAULT_GAUGE_TYPE,
            DEFAULT_GAUGE_WEIGHT,
            {"from": master_account, "gas_price": gas_strategy},
        )


def setup_distributor(dfx, distributor, master_account, new_master_account, rate):
    # Supply master account contract with rewards
    mint_dfx(dfx, TOTAL_DFX_REWARDS, master_account)

    # Distribute rewards to the distributor contract
    send_dfx(dfx, TOTAL_DFX_REWARDS, master_account, distributor)

    # Set rate to distribute 1,000,000 rewards (see spreadsheet)
    distributor.setRate(rate, {"from": new_master_account, "gas_price": gas_strategy})

    # Turn on distributions to gauges
    distributor.toggleDistributions(
        {"from": new_master_account, "gas_price": gas_strategy}
    )


def deposit_lp_tokens(lp_token, gauge, account):
    # deposit LP token into gauge
    amount = lp_token.balanceOf(account)
    lp_token.approve(gauge, amount, {"from": account, "gas_price": gas_strategy})
    gauge.deposit(amount, {"from": account, "gas_price": gas_strategy})

    # check that LP has been transfered
    assert lp_token.balanceOf(account) == 0


# Fetch all gauge addresses on controller which are not flagged as a killedGauge by distributor
def active_gauges(gauge_controller, dfx_distributor):
    num_gauges = gauge_controller.n_gauges()
    all_gauge_addresses = [gauge_controller.gauges(i) for i in range(0, num_gauges)]
    gauge_addresses = []
    for addr in all_gauge_addresses:
        if dfx_distributor.killedGauges(addr) == False:
            gauge_addresses.append(addr)
    return gauge_addresses
