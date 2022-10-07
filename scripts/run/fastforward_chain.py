#!/usr/bin/env python
from brownie import accounts, chain
from brownie.network import gas_price

from scripts import contracts
from scripts.helper import gas_strategy, get_addresses

WEEK = 86400 * 7

DEPLOY_ACCT = accounts.load('hardhat')

addresses = get_addresses()
gas_price(gas_strategy)


def main():
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    # fast-forward chain until end of epoch 1
    t0 = chain.time()
    t1 = (t0 + 2 * WEEK) // WEEK * WEEK - 10
    chain.sleep(t1 - t0)

    # distribute rewards to gauges
    gauge_addrs = [g.address for g in contracts.gauges()]
    dfx_distributor.distributeRewardToMultipleGauges(
        gauge_addrs, {'from': DEPLOY_ACCT, 'gas_price': gas_strategy})


if __name__ == '__main__':
    main()
