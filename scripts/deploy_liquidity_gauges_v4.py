#!/usr/bin/env python
from brownie import DfxUpgradeableProxy, LiquidityGaugeV4, accounts
from brownie.network import gas_price
from brownie.network.gas.strategies import LinearScalingStrategy
import json
import time

from scripts import addresses, helper


gas_strategy = LinearScalingStrategy('60 gwei', '150 gwei', 1.3)
gas_price(gas_strategy)


def main():
    print((
        'Script 3 of 3:\n\n'
        'NOTE: This script expects configuration for:\n'
        '\t1. VeBoostProxy address\n'
        '\t2. DfxDistributor address\n'
        '\t3. GaugeController address'
    ))

    acct = accounts.load('anvil')

    ve_boost_proxy_address = helper.get_json_address(
        "deployed_gaugecontroller", ["veBoostProxy"])
    gauge_controller_address = helper.get_json_address(
        "deployed_gaugecontroller", ["gaugeController"])
    dfx_distributor_address = helper.get_json_address(
        "deployed_distributor", ["distributor", "proxy"])

    raise Exception("WIP")

    print('--- Deploying Rewards-Only Gauges contract to Ethereum mainnet ---')
    lp_addresses = [
        ('CADC_USDC', addresses.DFX_CADC_USDC_LP),
        ('EURS_USDC', addresses.DFX_EURS_USDC_LP),
        ('XSGD_USDC', addresses.DFX_XSGD_USDC_LP),
        ('NZDS_USDC', addresses.DFX_NZDS_USDC_LP),
        ('TRYB_USDC', addresses.DFX_TRYB_USDC_LP),
        ('XIDR_USDC', addresses.DFX_XIDR_USDC_LP),
    ]
    output_data = {'gauges': {'amm': {}}}
    for label, lp_addr in lp_addresses:
        gauge = LiquidityGaugeV4.deploy(
            acct, lp_addr, {'from': acct, 'gas_price': gas_strategy})

        # deploy gauge logic
        gauge = LiquidityGaugeV4.deploy(
            {'from': acct, 'gas_price': gas_strategy})

        # deploy gauge behind proxy
        # NOTE: do we also want this for DFX? Why?
        gauge_initializer_calldata = gauge.initialize.encode_input(
            lp_addr,
            addresses.DFX_MULTISIG,
            addresses.DFX,
            addresses.veDFX,
            ve_boost_proxy_address,
            dfx_distributor_address,
        )
        dfx_upgradeable_proxy = DfxUpgradeableProxy.deploy(
            gauge.address,
            addresses.DFX_MULTISIG,
            gauge_initializer_calldata,
            {"from": acct, "gas_price": gas_strategy},
        )

        gauge_controller.add_gauge(
            addr, DEFAULT_GAUGE_TYPE, {'from': acct, 'gas_price': gas_strategy})

        output_data['gauges']['amm'][label] = {
            "logic": gauge.address,
            "proxy": dfx_upgradeable_proxy.address,
        }

        # print('--- Adding DFX AMM gauges ---')
        # gauge_addresses = _load_gauge_addresses() \
        #     if USE_LATEST_JSON else DEPLOYED_GAUGE_ADDRESSES

        # for _, addr in gauge_addresses:

    with open(f'./scripts/deployed_liquidity_gauges_v4_{int(time.time())}.json', 'w') as output_f:
        json.dump(output_data, output_f, indent=4)


if __name__ == '__main__':
    main()
