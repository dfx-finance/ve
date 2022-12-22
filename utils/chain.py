#!/usr/bin/env python
from datetime import datetime

from brownie import chain
from brownie.network.gas.strategies import LinearScalingStrategy

from .constants import WEEK


# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy("50 gwei", "200 gwei", 1.3)


# Fast-forwards chain state to delta (seconds) after (or before if negative)
# the next distribution epoch starts
def fastforward_chain_weeks(num_weeks, delta):
    t0 = chain.time()
    t1_dt = datetime.fromtimestamp((t0 + num_weeks * WEEK) // WEEK * WEEK + delta)
    fastforward_chain(t1_dt)


def fastforward_chain(until: datetime):
    chain.sleep(0)
    t0 = int(chain.time())
    chain.sleep(int(until.timestamp()) - t0)
    chain.mine()
    t1 = int(chain.time())

    orig = datetime.fromtimestamp(t0)
    new = datetime.fromtimestamp(t1)
    print("--- Fast-forward Chain -------------------------")
    print(f"Fastforwarded chain: {orig} --> {new}\n")
