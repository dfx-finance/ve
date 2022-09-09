#!/usr/bin/env python
from functools import reduce
import json
import operator
import os

from brownie import Contract, network, accounts, config
from brownie.network import show_active, gas_price
from brownie.network.gas.strategies import LinearScalingStrategy

from scripts import addresses


NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    'hardhat', 'development', 'ganache']
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    'mainnet-fork',
    'binance-fork',
    'matic-fork',
]

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('40 gwei', '120 gwei', 1.3)


def get_account(number=None):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if number:
        return accounts[number]
    if network.show_active() in config['networks']:
        account = accounts.add(config['wallets']['from_key'])
        return account
    return None


def encode_function_data(initializer=None, *args):
    '''Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.
        args (Any, optional):
        The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    '''
    if not len(args):
        args = b''

    if initializer:
        return initializer.encode_input(*args)

    return b''


def upgrade(
    account,
    proxy,
    newimplementation_address,
    proxy_admin_contract=None,
    initializer=None,
    *args
):
    transaction = None
    if proxy_admin_contract:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                newimplementation_address,
                encoded_function_call,
                {'from': account},
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address, newimplementation_address, {'from': account}
            )
    else:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy.upgradeToAndCall(
                newimplementation_address, encoded_function_call, {
                    'from': account}
            )
        else:
            transaction = proxy.upgradeTo(
                newimplementation_address, {'from': account})
    return transaction


# Return value from json file (by filename predicate) via a list of keys to drill down
def get_json_address(fn_predicate, keys):
    addresses_fn = [fn for fn in sorted(os.listdir('./scripts'))
                    if fn.startswith(fn_predicate) and fn.endswith('.json')][-1]
    if addresses_fn:
        with open(os.path.join('./scripts', addresses_fn), 'r') as json_f:
            json_data = json.load(json_f)
            return reduce(operator.getitem, keys, json_data)


def load_dfx_token():
    abi = json.load(open('./tests/abis/Dfx.json'))
    return Contract.from_abi('DFX', addresses.DFX, abi)


def network_info():
    connected_network = show_active()
    is_local_network = connected_network in ['ganache-cli', 'hardhat']
    if is_local_network:
        gas_price(gas_strategy)
    return connected_network, is_local_network


def get_addresses():
    connected_network, _ = network_info()
    return addresses.Polygon() if 'polygon' in connected_network else addresses.Ethereum()
