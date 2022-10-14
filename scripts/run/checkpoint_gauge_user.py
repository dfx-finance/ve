#!/usr/bin/env python
import json
import time

from scripts import contracts
from scripts.helper import get_addresses, gas_strategy, DEPLOY_ACCT


addresses = get_addresses()


def main():
    print((
        'NOTE: This script expects configuration for:\n'
        '\t1. DfxDistributor address\n'
    ))

    cadc_gauge = contracts.gauge(addresses.DFX_CADC_USDC_GAUGE)

    cadc_gauge.user_checkpoint('0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
        {'from': DEPLOY_ACCT, 'gas_price': gas_strategy})


if __name__ == '_main__':
    main()
