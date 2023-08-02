from brownie.network import show_active, gas_price

from scripts.utils.constants_addresses import Localhost, Polygon, Ethereum
from scripts.utils.gas import gas_strategy


def network_info():
    connected_network = show_active()
    is_local_network = connected_network in ["ganache-cli", "hardhat", "development"]
    if is_local_network:
        gas_price(gas_strategy)
    return connected_network, is_local_network


def get_network_addresses():
    connected_network, _ = network_info()

    if connected_network in ["hardhat", "development"]:
        return Localhost
    if connected_network == "polygon-main":
        return Polygon
    if connected_network in ["ethereum", "mainnet"]:
        return Ethereum
