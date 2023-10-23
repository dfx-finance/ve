#!/usr/bin/env python
import sys

from brownie.network.gas.strategies import LinearScalingStrategy

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy("32 gwei", "34 gwei", 1.3)


def verify_gas_strategy():
    print(
        f"Gas range: {int(gas_strategy.initial_gas_price / 1e9)} -> {int(gas_strategy.max_gas_price / 1e9)}"
    )
    if not input("Confirm? (y/n)  ").lower().strip() == "y":
        print("Canceled")
        sys.exit(1)
    print("Gas strategy verified!")
