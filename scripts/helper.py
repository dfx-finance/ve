#!/usr/bin/env python
from datetime import datetime
import json
import time

from brownie import accounts, chain, config, network, web3, Contract
from brownie.network import show_active, gas_price
from brownie.network.gas.strategies import LinearScalingStrategy

from dotenv import load_dotenv
from scripts import addresses, contracts

load_dotenv()

SECONDS_PER_YEAR = 365 * 24 * 60 * 60
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
gas_strategy = LinearScalingStrategy("32 gwei", "40 gwei", 1.3)


def get_account(number=None):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if number:
        return accounts[number]
    if network.show_active() in config["networks"]:
        account = accounts.add(config["wallets"]["from_key"])
        return account
    return None


def network_info():
    connected_network = show_active()
    is_local_network = connected_network in ["ganache-cli", "hardhat", "development"]
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


def load_dfx_token():
    addrs = get_addresses()
    abi = json.load(open("./tests/abis/Dfx.json"))
    return Contract.from_abi("DFX", addrs.DFX, abi)


###
### Log to file
###
def write_json_log(base_fn, output_data):
    fp = f"./scripts/{base_fn}_{int(time.time())}.json"
    with open(fp, "w") as output_f:
        json.dump(output_data, output_f, indent=4)
    return fp


###
### Log to console
###
def log_distributor_info():
    _addresses = get_addresses()
    dfx = contracts.erc20(_addresses.DFX)
    dfx_distributor = contracts.dfx_distributor(_addresses.DFX_DISTRIBUTOR)

    block_num = web3.eth.block_number
    block_timestamp = chain[block_num]["timestamp"]

    rewards_enabled = "on" if dfx_distributor.distributionsOn() else "off"
    distributor_dfx_balance = dfx.balanceOf(dfx_distributor.address)
    rate = dfx_distributor.rate()

    print("--- Distributor Info -------------------------")
    print(
        f"Block time (UTC): {datetime.utcfromtimestamp(block_timestamp)} ({block_num})\n"
        f"Distributions: {rewards_enabled}\n"
        f"Distributor mining epoch: {dfx_distributor.miningEpoch()}\n"
        f"Distributor epoch start time: {datetime.fromtimestamp(dfx_distributor.startEpochTime())}\n"
        f"Distributor balance (DFX): {dfx_distributor.address} ({distributor_dfx_balance / 1e18})\n"
        f"Distributor rate (DFX per second): {rate} ({rate / 1e18})\n"
        f"Distributor rate (DFX per year): {rate * SECONDS_PER_YEAR} ({rate * SECONDS_PER_YEAR / 1e18})\n"
    )


def log_gauges_info(gauge_addresses):
    _addresses = get_addresses()
    dfx = contracts.erc20(_addresses.DFX)
    gauge_controller = contracts.gauge_controller(_addresses.GAUGE_CONTROLLER)

    print("--- Gauges Info -------------------------")
    weights = [gauge_controller.get_gauge_weight(addr) for _, addr in gauge_addresses]
    total_weight = sum(weights)
    for i, weight in enumerate(weights):
        label, addr = gauge_addresses[i]
        g = contracts.gauge(addr)
        raw_dfx_rate = g.reward_data(_addresses.DFX)[3]
        undistributed_dfx_rewards = (raw_dfx_rate * 604800) / 1e18
        rewards = [f"{undistributed_dfx_rewards} DFX"]
        dfx_balance = dfx.balanceOf(g) / 1e18

        weight_pct = weight / total_weight * 100 if total_weight else 0
        print(
            f"{label} gauge weight: {weight_pct:.2f}% ({(' / ').join(rewards)}) (DFX balance: {dfx_balance})"
        )
    print("")


def log_gauge_weights(gauge_addresses):
    _addresses = get_addresses()
    gauge_controller = contracts.gauge_controller(_addresses.GAUGE_CONTROLLER)

    print("--- Gauges Weights -------------------------")
    weights = [gauge_controller.get_gauge_weight(addr) for _, addr in gauge_addresses]
    for i, weight in enumerate(weights):
        label, _ = gauge_addresses[i]
        print(f"{label} gauge weight: {weight}")


###
### Proxy upgrades
###
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
    *args,
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
