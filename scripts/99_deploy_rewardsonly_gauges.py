from brownie import RewardsOnlyGauge, accounts
from brownie.network import gas_price
from brownie.network.gas.strategies import LinearScalingStrategy
import json
import time

import scripts.addresses as addresses


gas_strategy = LinearScalingStrategy('60 gwei', '150 gwei', 1.3)
gas_price(gas_strategy)


def main():
    acct = accounts.load('anvil')

    print('--- Deploying Rewards-Only Gauges contract to Ethereum mainnet ---')
    lp_addresses = [
        ('CADC_USDC', addresses.DFX_CADC_USDC_LP),
        ('EUROC_USDC', addresses.DFX_EUROC_USDC_LP),
        ('XSGD_USDC', addresses.DFX_XSGD_USDC_LP),
        ('NZDS_USDC', addresses.DFX_NZDS_USDC_LP),
        ('TRYB_USDC', addresses.DFX_TRYB_USDC_LP),
        ('XIDR_USDC', addresses.DFX_XIDR_USDC_LP),
    ]

    output_data = {'gauges': {'amm': {}}}
    for label, lp_addr in lp_addresses:
        gauge = RewardsOnlyGauge.deploy(
            acct, lp_addr, {'from': acct, 'gas_price': gas_strategy})
        output_data['gauges']['amm'][label] = gauge.address

    with open(f'./scripts/deployed_rewards_only_gauges_{int(time.time())}.json', 'w') as output_f:
        json.dump(output_data, output_f, indent=4)


if __name__ == '__main__':
    main()
