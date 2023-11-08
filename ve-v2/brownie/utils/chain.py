#!/usr/bin/env python
from datetime import datetime

from brownie import chain

from .constants import WEEK


# Fast-forwards chain state to delta (seconds) after (or before if negative)
# the next distribution epoch starts
def fastforward_chain_weeks(num_weeks, delta=0, log=False):
    num_weeks += 1
    t0 = chain.time()
    t1 = (t0 + num_weeks * WEEK) // WEEK * WEEK + delta
    fastforward_chain(t1, log)


def fastforward_chain(until: int, log=False):
    t0 = int(chain.time())
    delta = until - t0
    chain.sleep(delta)
    chain.mine()

    if log:
        t1 = int(chain.time())
        orig = datetime.fromtimestamp(t0)
        new = datetime.fromtimestamp(t1)
        print("--- Fast-forward Chain -------------------------")
        print(f"Fastforwarded chain: {orig} --> {new}")


# Fast-forwards chain state to delta (seconds) after (or before if negative)
# the next distribution epoch starts
def fastforward_chain_weeks_anvil(num_weeks, delta, log=False):
    num_weeks += 1
    t0 = int(chain.time())
    t1 = int((t0 + num_weeks * WEEK) // WEEK * WEEK + delta)
    fastforward_chain_anvil(t1, log)


def fastforward_chain_anvil(t1: int, log=False):
    t0 = int(chain.time())
    delta = t1 - t0

    start_offset = chain._time_offset
    chain.sleep(delta)
    chain._time_offset = start_offset + delta

    if log:
        orig = datetime.fromtimestamp(t0)
        new = datetime.fromtimestamp(t1)
        print("--- Fast-forward Chain -------------------------")
        print(f"Fastforwarded chain: {orig} --> {new}\n")
