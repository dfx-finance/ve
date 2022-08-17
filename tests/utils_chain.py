#!/usr/bin/env python
import brownie

from utils_ve import WEEK


# Fast-forwards chain state to delta (seconds) after (or before if negative)
# the next distribution epoch starts
def fastforward_chain(num_weeks, delta):
    t0 = brownie.chain.time()
    t1 = (t0 + num_weeks * WEEK) // WEEK * WEEK + delta
    brownie.chain.sleep(t1 - t0)
    brownie.chain.mine()
