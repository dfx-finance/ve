#!/usr/bin/env python
from brownie import accounts

from scripts import contracts
from scripts.helper import get_addresses, gas_strategy

DEPLOY_ACCT = accounts.load('deployve')

addresses = get_addresses()


def main():
    print((
        'NOTE: This script expects configuration for:\n'
        '\t1. DfxDistributor address\n'
    ))
    dfx_distributor = contracts.dfx_distributor()

    # Public function to advance epoch & recalculate reward rate when previous
    # epoch has expired
    # NOTE: returns a "108" error when rate has been updated for this epoch,
    # either via this function or `distributeReward/distributorRewardToMultipleGauges`
    dfx_distributor.updateMiningParameters(
        {'from': DEPLOY_ACCT, 'gas_price': gas_strategy})


if __name__ == '_main__':
    main()
