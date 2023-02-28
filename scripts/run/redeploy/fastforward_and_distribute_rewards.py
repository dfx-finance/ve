#!/usr/bin/env python
from datetime import datetime, timezone

from brownie import accounts, chain
from scripts import contracts
from scripts.helper import (
    gas_strategy,
    get_addresses,
    log_distributor_info,
    log_gauges_info,
)
from utils.chain import fastforward_chain

addresses = get_addresses()

GAUGE_ADDRESSES = [
    ("CADC_USDC", addresses.DFX_CADC_USDC_GAUGE),
    ("EUROC_USDC", addresses.DFX_EUROC_USDC_GAUGE),
    ("GYEN_USDC", addresses.DFX_GYEN_USDC_GAUGE),
    ("NZDS_USDC", addresses.DFX_NZDS_USDC_GAUGE),
    ("TRYB_USDC", addresses.DFX_TRYB_USDC_GAUGE),
    ("XIDR_USDC", addresses.DFX_XIDR_USDC_GAUGE),
    ("XSGD_USDC", addresses.DFX_XSGD_USDC_GAUGE),
]
DEPLOY_ACCT = accounts[0]


def main():
    print(f"Chain time (UTC): {datetime.utcfromtimestamp(chain.time())}")

    fastforward_chain(until=datetime(2022, 12, 29, 0, 0, 30, 0, tzinfo=timezone.utc))

    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    # Fetch enabled gauge addresses
    num_gauges = gauge_controller.n_gauges()
    all_gauge_addresses = [gauge_controller.gauges(i) for i in range(0, num_gauges)]
    gauge_addresses = []
    for addr in all_gauge_addresses:
        if dfx_distributor.killedGauges(addr) == False:
            gauge_addresses.append(addr)

    # Distribute gauge rewards
    dfx_distributor.distributeRewardToMultipleGauges(
        gauge_addresses, {"from": DEPLOY_ACCT, "gas_price": gas_strategy}
    )

    log_distributor_info()
    log_gauges_info(GAUGE_ADDRESSES)
