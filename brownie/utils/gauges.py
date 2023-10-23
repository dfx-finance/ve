#!/usr/bin/env python
from .constants import (
    DEFAULT_TYPE_WEIGHT,
    DEFAULT_GAUGE_TYPE,
    DEFAULT_GAUGE_WEIGHT,
)
from . import contracts
from .gas import gas_strategy
from .helper import mint_dfx, send_dfx


def setup_gauge_controller(gauge_controller, gauges, multisig_0):
    gauge_controller.add_type(
        "AMM Liquidity Pools",
        DEFAULT_TYPE_WEIGHT,
        {"from": multisig_0, "gas_price": gas_strategy},
    )
    for gauge in gauges:
        gauge_controller.add_gauge(
            gauge,
            DEFAULT_GAUGE_TYPE,
            DEFAULT_GAUGE_WEIGHT,
            {"from": multisig_0, "gas_price": gas_strategy},
        )


def setup_distributor(
    dfx, distributor, deploy_account, multisig_0, rate, total_rewards_amount
):
    # Distribute rewards to the distributor contract
    send_dfx(dfx, total_rewards_amount, deploy_account, distributor)

    # Set rate to distribute 1,000,000 rewards (see spreadsheet)
    distributor.setRate(rate, {"from": multisig_0, "gas_price": gas_strategy})

    # Turn on distributions to gauges
    distributor.toggleDistributions({"from": multisig_0, "gas_price": gas_strategy})


def deposit_lp_tokens(lp_token, gauge, account):
    # deposit LP token into gauge
    amount = lp_token.balanceOf(account)
    assert amount > 0

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

    gauges = [contracts.gauge(addr) for addr in gauge_addresses]
    return gauges
