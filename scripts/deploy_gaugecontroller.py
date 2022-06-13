from brownie import GaugeController, accounts
from brownie.network import gas_price
from brownie.network.gas.strategies import LinearScalingStrategy

import scripts.addresses as addresses


gas_strategy = LinearScalingStrategy("60 gwei", "150 gwei", 1.3)
gas_price(gas_strategy)


def main():
    acct = accounts.load('ganache')
    GaugeController.deploy(
        addresses.DFX, addresses.VOTE_ESCROW, {'from': acct, 'gas_price': gas_strategy})
