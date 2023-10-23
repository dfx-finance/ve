from brownie.network import show_active, gas_price

from .constants_addresses import (
    Arbitrum,
    Ethereum,
    EthereumLocalhost,
    Mumbai,
    Polygon,
    Sepolia,
)
from .gas import gas_strategy


class NetworkAddresses:
    pass


class ConnectedNetwork:
    name: str
    addresses: NetworkAddresses
    is_local: bool

    def __init__(self, name: str, addresses: NetworkAddresses, is_local: bool):
        self.name = name
        self.addresses = addresses
        self.is_local = is_local


def get_network_addresses(connected_network):
    if connected_network in ["ethereum", "mainnet"]:
        return Ethereum
    if connected_network in ["arbitrum"]:
        return Arbitrum
    if connected_network in ["polygon-main"]:
        return Polygon
    if connected_network in ["sepolia", "sepolia-dev"]:
        return Sepolia
    if connected_network in ["polygon-test"]:
        return Mumbai
    if connected_network in ["hardhat", "development"]:
        return EthereumLocalhost


def network_info() -> ConnectedNetwork:
    name = show_active()
    addresses = get_network_addresses(name)
    is_local_network = name in ["ganache-cli", "hardhat", "development"]
    if is_local_network:
        gas_price(gas_strategy)
    return ConnectedNetwork(name, addresses, is_local_network)
