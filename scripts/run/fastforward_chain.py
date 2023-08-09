#!/usr/bin/env python
from brownie import chain
from brownie.network import gas_price

from datetime import datetime, timezone

from utils.chain import fastforward_chain
from utils.constants import WEEK
from utils.gas import gas_strategy
from utils.network import get_network_addresses


addresses = get_network_addresses()
gas_price(gas_strategy)


class FastforwardTime:
    def week(chain_time, n=1):
        return chain_time + n * WEEK

    def rounded_week(chain_time, n=1, delta=0):
        return (chain_time + n * WEEK) // WEEK * WEEK + delta

    def hours(chain_time, _hours, delta=0):
        return chain_time + 60 * 60 * _hours + delta

    def until(target):
        return int(target.timestamp())


def main():
    # fast-forward chain until end of epoch 1
    endtime = datetime(2023, 3, 2, 0, 0, 0, 0, tzinfo=timezone.utc)
    t1 = FastforwardTime.until(target=endtime)
    # t1 = 1800 # 30-mins
    # t1 = FastforwardTime.week(t0)
    # t1 = FastforwardTime.hours(t0, 24)

    fastforward_chain(t1)


if __name__ == "__main__":
    main()
