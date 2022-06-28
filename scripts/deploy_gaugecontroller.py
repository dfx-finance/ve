import json
import os
from brownie import GaugeController, accounts
from brownie.network import gas_price
from brownie.network.gas.strategies import LinearScalingStrategy
import time

import scripts.addresses as addresses

USE_LATEST_JSON = True
DEFAULT_GAUGE_TYPE_NAME = 'Liquidity'
DEPLOYED_GAUGE_ADDRESSES = [
    ('CADC_USDC', None),
    ('EURS_USDC', None),
    ('XSGD_USDC', None),
    ('NZDS_USDC', None),
    ('TRYB_USDC', None),
    ('XIDR_USDC', None),
]
# Type 0 for Ethereum stableswap pools (https://curve.readthedocs.io/dao-gauges.html#gauge-types)
DEFAULT_GAUGE_TYPE = 0

gas_strategy = LinearScalingStrategy('60 gwei', '150 gwei', 1.3)
gas_price(gas_strategy)


def _load_gauge_addresses():
    gauge_addresses = []
    gauge_fn = [fn for fn in os.listdir('./scripts')
                if fn.startswith('deployed_gauges_') and fn.endswith('.json')][-1]
    if gauge_fn:
        with open(os.path.join('./scripts', gauge_fn), 'r') as json_f:
            gauges_data = json.load(json_f)
            for label, gauge_addr in gauges_data['gauges']['amm'].items():
                gauge_addresses.append((label, gauge_addr))
    return gauge_addresses


def main():
    acct = accounts.load('anvil')

    print('--- Deploying Gauge Controller contract to Ethereum mainnet ---')
    gauge_controller = GaugeController.deploy(
        addresses.DFX, addresses.VOTE_ESCROW, {'from': acct, 'gas_price': gas_strategy})

    print('----- Configure Gauge Controller with "Liquidity" type')
    gauge_controller.add_type(
        DEFAULT_GAUGE_TYPE_NAME, 1e18, {'from': acct, 'gas_price': gas_strategy})

    print('--- Adding DFX AMM gauges ---')
    gauge_addresses = _load_gauge_addresses() \
        if USE_LATEST_JSON else DEPLOYED_GAUGE_ADDRESSES

    for _, addr in gauge_addresses:
        gauge_controller.add_gauge(
            addr, DEFAULT_GAUGE_TYPE, {'from': acct, 'gas_price': gas_strategy})

    output_data = {'gaugeController': gauge_controller.address}
    with open(f'./scripts/deployed_gaugecontroller_{time.time()}.json', 'w') as output_f:
        json.dump(output_data, output_f, indent=4)
