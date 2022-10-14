#!/usr/bin/env python
import json
import time

from scripts import contracts
from scripts.helper import get_addresses, gas_strategy, DEPLOY_ACCT


addresses = get_addresses()

output_data = {'distributor': {'proxy': None, 'distributionsOn': None}}


def main():
    print((
        'NOTE: This script expects configuration for:\n'
        '\t1. DfxDistributor address\n'
    ))

    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    # Turn on distributions to gauges
    dfx_distributor.toggleDistributions(
        {'from': DEPLOY_ACCT, 'gas_price': gas_strategy})

    output_data['distributor'] = {
        'proxy': dfx_distributor.address,
        'distributionsOn': dfx_distributor.distributionsOn(),
    }
    with open(f'./scripts/toggled_gauges_{int(time.time())}.json', 'w') as output_f:
        json.dump(output_data, output_f, indent=4)


if __name__ == '_main__':
    main()
