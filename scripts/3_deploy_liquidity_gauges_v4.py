#!/usr/bin/env python
import json
import time

import brownie
from brownie import DfxUpgradeableProxy, LiquidityGaugeV4, accounts
from brownie.network import gas_price

from scripts import addresses, contracts
from scripts.helper import gas_strategy

gas_price(gas_strategy)

DEFAULT_GAUGE_TYPE = 0
DEFAULT_GAUGE_WEIGHT = 1e18

DEPLOY_ACCT = accounts.load('hardhat')
PROXY_MULTISIG = accounts[7]

output_data = {'gauges': {'amm': {}}}


def main():
    print((
        'Script 3 of 3:\n\n'
        'NOTE: This script expects configuration for:\n'
        '\t1. VeBoostProxy address\n'
        '\t2. DfxDistributor address\n'
        '\t3. GaugeController address'
    ))

    veboost_proxy = contracts.veboost_proxy()
    gauge_controller = contracts.gauge_controller()
    dfx_distributor = contracts.dfx_distributor()

    print('--- Deploying Liquidity Gauges (v4) contract to Ethereum mainnet ---')
    lp_addresses = [
        ('CADC_USDC', addresses.DFX_CADC_USDC_LP),
        ('EUROC_USDC', addresses.DFX_EUROC_USDC_LP),
        ('EURS_USDC', addresses.DFX_EURS_USDC_LP),
        ('NZDS_USDC', addresses.DFX_NZDS_USDC_LP),
        ('TRYB_USDC', addresses.DFX_TRYB_USDC_LP),
        ('XIDR_USDC', addresses.DFX_XIDR_USDC_LP),
        ('XSGD_USDC', addresses.DFX_XSGD_USDC_LP),
    ]

    for label, lp_addr in lp_addresses:
        # deploy gauge logic
        gauge = LiquidityGaugeV4.deploy(
            {'from': DEPLOY_ACCT, 'gas_price': gas_strategy})

        # deploy gauge behind proxy
        gauge_initializer_calldata = gauge.initialize.encode_input(
            lp_addr,
            DEPLOY_ACCT,
            addresses.DFX,
            addresses.VOTE_ESCROW,
            veboost_proxy.address,
            dfx_distributor.address,
        )
        dfx_upgradeable_proxy = DfxUpgradeableProxy.deploy(
            gauge.address,
            PROXY_MULTISIG,
            gauge_initializer_calldata,
            {'from': DEPLOY_ACCT, 'gas_price': gas_strategy},
        )

        gauge_controller.add_gauge(
            dfx_upgradeable_proxy.address, DEFAULT_GAUGE_TYPE, DEFAULT_GAUGE_WEIGHT, {'from': DEPLOY_ACCT, 'gas_price': gas_strategy})

        output_data['gauges']['amm'][label] = {
            'logic': gauge.address,
            'proxy': dfx_upgradeable_proxy.address,
        }

    with open(f'./scripts/deployed_liquidity_gauges_v4_{int(time.time())}.json', 'w') as output_f:
        json.dump(output_data, output_f, indent=4)


if __name__ == '__main__':
    main()
