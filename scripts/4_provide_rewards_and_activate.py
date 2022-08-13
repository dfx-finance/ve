#!/usr/bin/env python
import brownie
from brownie import accounts, Contract
from brownie.network.web3 import web3
import json

from scripts import addresses
from scripts.helper import gas_strategy, get_json_address

EMISSION_RATE = 1.60345055442863e16
TOTAL_DFX_REWARDS = 1_248_560 * 1e18


def load_dfx_token():
    # Load existing DFX ERC20 from mainnet fork
    abi = json.load(open('./tests/abis/Dfx.json'))
    return Contract.from_abi('DFX', addresses.DFX, abi)


def send_dfx(dfx, amount, from_account, to_account):
    dfx.transfer(to_account, amount, {
                 'from': from_account, 'gas_price': gas_strategy})
    print('Sender account DFX balance:',
          dfx.balanceOf(from_account) / 1e18)


def main():
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
        EMISSION_RATE, {'from': addresses.DFX_MULTISIG, 'gas_price': gas_strategy})

    # Turn on distributions to gauges
    distributor.toggleDistributions(
        {'from': addresses.DFX_MULTISIG, 'gas_price': gas_strategy})

    print(distributor.distributionsOn())


if __name__ == '_main__':
    main()
