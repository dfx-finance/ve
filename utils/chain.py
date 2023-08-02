#!/usr/bin/env python
from datetime import datetime

from brownie import chain
from brownie.network.gas.strategies import LinearScalingStrategy

from utils.constants import WEEK


# Fast-forwards chain state to delta (seconds) after (or before if negative)
# the next distribution epoch starts
def fastforward_chain_weeks(num_weeks, delta):
    t0 = chain.time()
    t1_dt = datetime.fromtimestamp((t0 + num_weeks * WEEK) // WEEK * WEEK + delta)
    fastforward_chain(t1_dt)


def fastforward_chain(until: datetime):
    chain.sleep(0)
    chain.mine()

    t0 = int(chain.time())
    chain.sleep(int(until.timestamp()) - t0)
    chain.mine()
    t1 = int(chain.time())

    orig = datetime.fromtimestamp(t0)
    new = datetime.fromtimestamp(t1)
    print("--- Fast-forward Chain -------------------------")
    print(f"Fastforwarded chain: {orig} --> {new}\n")
