#!/usr/bin/env python
import brownie
from brownie import accounts, Contract
from brownie.network.web3 import web3
import json
import time

from scripts import addresses
from scripts.helper import gas_strategy, get_json_address

REWARDS_RATE = 1.60345055442863e16
TOTAL_DFX_REWARDS = 1_248_560 * 1e18

output_data = {'distributor': {'proxy': None, 'distributionsOn': None}}


def load_dfx_token():
    abi = json.load(open('./tests/abis/Dfx.json'))
    return Contract.from_abi('DFX', addresses.DFX, abi)


def send_dfx(dfx, amount, from_account, to_account):
    dfx.transfer(to_account, amount, {
                 'from': from_account, 'gas_price': gas_strategy})
    print('Sender account DFX balance:',
          dfx.balanceOf(from_account) / 1e18)


def main():
    print((
        'Script 4 of 4:\n\n'
        'NOTE: This script expects configuration for:\n'
        '\t1. DfxDistributor address\n'
        '\t2. Total amount of rewards to provide\n'
        '\t3. New DFX token rewards per second\n'
    ))

    acct = accounts.load('anvil')
    dfx = load_dfx_token()

    dfx_distributor_address = get_json_address(
        'deployed_distributor', ['distributor', 'proxy'])

    distributor = brownie.interface.IDfxDistributor(
        dfx_distributor_address)

    # unlock multisig account
    brownie.rpc.unlock_account(addresses.DFX_MULTISIG)

    # provide multisig with ether
    acct.transfer(addresses.DFX_MULTISIG, "1 ether")

    # Distribute rewards to the distributor contract
    send_dfx(dfx, TOTAL_DFX_REWARDS, addresses.DFX_MULTISIG, distributor)

    # Set rate to distribute 1,000,000 rewards (see spreadsheet)
    distributor.setRate(
        REWARDS_RATE, {'from': addresses.DFX_MULTISIG, 'gas_price': gas_strategy})

    # Turn on distributions to gauges
    distributor.toggleDistributions(
        {'from': addresses.DFX_MULTISIG, 'gas_price': gas_strategy})

    output_data['distributor'] = {
        'proxy': dfx_distributor_address,
        'rewardsSupplied': TOTAL_DFX_REWARDS,
        'rewardsRate': REWARDS_RATE,
        'totalRewards': dfx.balanceOf(distributor),
        'distributionsOn': distributor.distributionsOn(),
    }
    with open(f'./scripts/provided_rewards_and_activated_{int(time.time())}.json', 'w') as output_f:
        json.dump(output_data, output_f, indent=4)


if __name__ == '_main__':
    main()
