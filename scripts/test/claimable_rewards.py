#!/usr/bin/env python
from brownie import chain

from utils import contracts
from utils.gauges import active_gauges
from utils.network import get_network_addresses


addresses = get_network_addresses()

TEST_ADDR = "0x29770812d00E6C24dE42D7F51274A05e6A3C04F0"  # any user address
DAY = 24 * 60 * 60


def main():
    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)
    distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    gauges = active_gauges(gauge_controller, distributor)
    cadc_usdc_lpt = contracts.erc20(addresses.DFX_CADC_USDC_LP)
    cadc_gauge = gauges[0]

    # get starting chain time
    chain.sleep(0)

    # get the prior amount of rewards claimable for epoch
    base = cadc_gauge.claimable_reward(TEST_ADDR, addresses.DFX)
    lpt = cadc_gauge.balanceOf(TEST_ADDR)
    lpt_total = cadc_usdc_lpt.balanceOf(cadc_gauge)

    # fast-forward 24 hours
    chain.sleep(DAY)
    chain.mine()

    rewards = cadc_gauge.claimable_reward(TEST_ADDR, addresses.DFX)

    print(f"LPT in Gauge: {lpt / 1e18} (total: {lpt_total / 1e18})")
    print("LPT %:", lpt / lpt_total * 100)
    print("Past 24-hours rewards:", (rewards - base) / 1e18)


if __name__ == "_main__":
    main()
