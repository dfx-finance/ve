#!/usr/bin/env python
import brownie
from brownie.network.gas.strategies import LinearScalingStrategy

from .constants import WEEK


# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('50 gwei', '200 gwei', 1.3)

# Fast-forwards chain state to delta (seconds) after (or before if negative)
# the next distribution epoch starts


def fastforward_chain(num_weeks, delta):
    t0 = brownie.chain.time()
    t1 = (t0 + num_weeks * WEEK) // WEEK * WEEK + delta
    brownie.chain.sleep(t1 - t0)
    brownie.chain.mine()
