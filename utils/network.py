from brownie.network import show_active, gas_price

from .constants_addresses import Localhost, Polygon, Ethereum, Sepolia, Mumbai
from .gas import gas_strategy


def network_info():
    connected_network = show_active()
    is_local_network = connected_network in ["ganache-cli", "hardhat", "development"]
    if is_local_network:
        gas_price(gas_strategy)
    return connected_network, is_local_network


def get_network_addresses():
    connected_network, _ = network_info()

    if connected_network in ["ethereum", "mainnet"]:
        return Ethereum
    if connected_network in ["polygon-main"]:
        return Polygon
    if connected_network in ["sepolia", "sepolia-dev"]:
        return Sepolia
    if connected_network in ["polygon-test"]:
        return Mumbai
    if connected_network in ["hardhat", "development"]:
        return Localhost
