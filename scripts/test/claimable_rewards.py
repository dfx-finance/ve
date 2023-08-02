#!/usr/bin/env python
from brownie import accounts, chain

from utils import contracts
from utils.account import impersonate
from utils.network import get_network_addresses


addresses = get_network_addresses()

TEST_ADDR = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"  # any user address
DAY = 24 * 60 * 60


def main():
    tester = impersonate(TEST_ADDR)
    gauges = contracts.gauges()
    cadc_usdc_lpt = contracts.erc20(addresses.DFX_CADC_USDC_LP)
    cadc_gauge = gauges[0]

    # get starting chain time
    chain.sleep(0)
    t0 = int(chain.time())

    # get the prior amount of rewards claimable for epoch
    base = cadc_gauge.claimable_reward(tester, addresses.DFX)
    lpt = cadc_gauge.balanceOf(tester)
    lpt_total = cadc_usdc_lpt.balanceOf(cadc_gauge)

    # fast-forward 24 hours
    chain.sleep(DAY)
    chain.mine()
    rewards = cadc_gauge.claimable_reward(tester, addresses.DFX)

    print(base / 1e18, rewards / 1e18)
    print(f"LPT in Gauge: {lpt / 1e18} (total: {lpt_total / 1e18})")
    print("LPT %:", lpt / lpt_total * 100)
    print("Past 24-hours rewards:", (rewards - base) / 1e18)


if __name__ == "_main__":
    main()
