#!/usr/bin/env python
# 1. Stop distribution to all gauges
#    - Rewards within gauge will remain available to _any_ user who continues to stake through following epoch
# 2. Withdraw all DFX ERC20 from distributor gauge to multisig
import brownie
from brownie import accounts
from brownie.network import gas_price

from scripts import addresses
from scripts.helper import get_json_address, gas_strategy


DEPLOY_ACCT = accounts.load('hardhat')
DFX_MULTISIG = accounts.at(address=addresses.DFX_MULTISIG, force=True)

gas_price(gas_strategy)


def main():
    dfx_distributor_address = get_json_address(
        'deployed_distributor', ['distributor', 'proxy'])
    # cadc_gauge_address = get_json_address(
    #     'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'CADC_USDC', 'proxy'])
    # eurs_gauge_address = get_json_address(
    #     'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'EURS_USDC', 'proxy'])
    # euroc_gauge_address = get_json_address(
    #     'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'EUROC_USDC', 'proxy'])
    # nzds_gauge_address = get_json_address(
    #     'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'NZDS_USDC', 'proxy'])
    # tryb_gauge_address = get_json_address(
    #     'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'TRYB_USDC', 'proxy'])
    # xidr_gauge_address = get_json_address(
    #     'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'XIDR_USDC', 'proxy'])
    # xsgd_gauge_address = get_json_address(
    #     'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'XSGD_USDC', 'proxy'])

    distributor = brownie.interface.IDfxDistributor(dfx_distributor_address)
    distributor.toggleDistributions(
        {'from': DFX_MULTISIG, 'gas_price': gas_strategy})


if __name__ == '__main__':
    pass
