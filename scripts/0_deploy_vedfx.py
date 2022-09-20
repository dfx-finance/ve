#!/usr/bin/env python
from brownie import accounts, VeDFX
from brownie.network import gas_price
import eth_abi
import json
import time

from scripts.helper import gas_strategy, network_info


gas_price(gas_strategy)
connected_network, _ = network_info()


# Configs
if connected_network == 'hardhat':
    DFX = '0x888888435FDe8e7d4c54cAb67f206e4199454c60'
if connected_network == 'polygon-main':
    DFX = '0xE7804D91dfCDE7F776c90043E03eAa6Df87E6395'


def main():
    acct = accounts.load('deployve')

    print(f'--- Deploying veDFX contract to {connected_network} ---')

    output_data = {'veDFX': None}

    vedfx_params = eth_abi.encode_abi(['address', 'string', 'string', 'string'],
                                      (DFX, 'Vote-escrowed DFX', 'veDFX',
                                       'veDFX_1.0.0')).hex()
    vedfx = VeDFX.deploy(DFX, 'Vote-escrowed DFX', 'veDFX',
                         'veDFX_1.0.0', {'from': acct, 'gas_price': gas_strategy})
    output_data['veDFX'] = vedfx.address
    output_data['veDFXParams'] = vedfx_params

    with open(f'./scripts/deployed_vedfx_{int(time.time())}.json', 'w') as output_f:
        json.dump(output_data, output_f, indent=4)


if __name__ == '__main__':
    main()
