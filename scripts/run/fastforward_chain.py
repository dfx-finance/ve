#!/usr/bin/env python
from brownie import chain
from brownie.network import gas_price

from datetime import datetime, timezone

from scripts.helper import gas_strategy, get_addresses
from utils.constants import WEEK


addresses = get_addresses()
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
    chain.sleep(0)
    t0 = int(chain.time())

    # endtime = datetime(2022, 11, 3, 20, 0, 0, 0, tzinfo=timezone.utc)
    # t1 = FastforwardTime.until(target=endtime)
    # t1 = 1800 # 30-mins
    # t1 = FastforwardTime.week(t0)
    t1 = FastforwardTime.hours(t0, 24)

    print(t0)
    chain.sleep(t1 - t0)
    chain.mine()
    print(datetime.utcfromtimestamp(chain.time()))


if __name__ == "__main__":
    main()
