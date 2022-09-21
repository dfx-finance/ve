#!/usr/bin/env python
from brownie import accounts

from scripts import contracts
from scripts.helper import get_addresses, gas_strategy

DEPLOY_ACCT = accounts.load('hardhat')
# DEPLOY_ACCT = accounts.load('deployve')

addresses = get_addresses()


def main():
    print((
        'NOTE: This script expects configuration for:\n'
        '\t1. GaugeDistributor address\n'
        '\t2. DfxDistributor address\n'
    ))
    gauge_controller = contracts.gauge_controller()
    dfx_distributor = contracts.dfx_distributor()

    # Fetch enabled gauge addresses
    num_gauges = gauge_controller.n_gauges()
    all_gauge_addresses = [
        gauge_controller.gauges(i) for i in range(0, num_gauges)]
    gauge_addresses = []
    for addr in all_gauge_addresses:
        if dfx_distributor.killedGauges(addr) == False:
            gauge_addresses.append(addr)

    # Distribute gauge rewards
    dfx_distributor.distributeRewardToMultipleGauges(
        gauge_addresses, {'from': DEPLOY_ACCT, 'gas_price': gas_strategy})


if __name__ == '_main__':
    main()
