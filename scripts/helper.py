#!/usr/bin/env python
import json
import os

from brownie import Contract, network, accounts, config
from brownie.network import show_active, gas_price
from brownie.network.gas.strategies import LinearScalingStrategy

from dotenv import load_dotenv
from scripts import addresses

load_dotenv()


NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "hardhat",
    "development",
    "ganache",
    "ganache-cli",
]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]
# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy("72 gwei", "80 gwei", 1.3)

# Script wallets
DEPLOY_ACCT_WALLET = os.getenv("DEPLOY_WALLET", "hardhat")
DEPLOY_ACCT = accounts.load(DEPLOY_ACCT_WALLET)
# PROXY_MULTISIG = accounts[7] if DEPLOY_ACCT_WALLET == 'hardhat' else accounts.load('deployve-proxyadmin')
GOVERNOR_MULTISIG = DEPLOY_ACCT
GUARDIAN_MULTISIG = DEPLOY_ACCT


def get_account(number=None):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if number:
        return accounts[number]
    if network.show_active() in config["networks"]:
        account = accounts.add(config["wallets"]["from_key"])
        return account
    return None


def encode_function_data(initializer=None, *args):
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.
        args (Any, optional):
        The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
    if not len(args):
        args = b""

    if initializer:
        return initializer.encode_input(*args)

    return b""


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
                {"from": account},
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address, newimplementation_address, {"from": account}
            )
    else:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy.upgradeToAndCall(
                newimplementation_address, encoded_function_call, {"from": account}
            )
        else:
            transaction = proxy.upgradeTo(newimplementation_address, {"from": account})
    return transaction


def load_dfx_token():
    addrs = get_addresses()
    abi = json.load(open("./tests/abis/Dfx.json"))
    return Contract.from_abi("DFX", addrs.DFX, abi)


def load_usdc_token():
    addrs = get_addresses()
    abi = json.load(open("./tests/abis/Usdc.json"))
    return Contract.from_abi("USDC", addrs.USDC, abi)


def network_info():
    connected_network = show_active()
    is_local_network = connected_network in ["ganache-cli", "hardhat"]
    if is_local_network:
        gas_price(gas_strategy)
    return connected_network, is_local_network


def get_addresses():
    connected_network, _ = network_info()

    if connected_network in ["hardhat", "development"]:
        return addresses.Localhost
    if connected_network == "polygon-main":
        return addresses.Polygon
    if connected_network in ["ethereum", "mainnet"]:
        return addresses.Ethereum
