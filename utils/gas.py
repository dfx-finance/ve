#!/usr/bin/env python
from brownie.network.gas.strategies import LinearScalingStrategy

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy("100 gwei", "120 gwei", 1.5)
