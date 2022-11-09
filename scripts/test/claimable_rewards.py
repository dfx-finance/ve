#!/usr/bin/env python
from brownie import accounts, chain

from scripts import contracts
from scripts.helper import get_addresses, gas_strategy, load_dfx_token, load_usdc_token


addresses = get_addresses()

TEST_ADDR = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"  # any user address
DAY = 24 * 60 * 60


def main():
    tester = accounts.at(address=TEST_ADDR, force=True)
    gauges = contracts.gauges()
    tryb_usdc_lpt = contracts.erc20(addresses.DFX_TRYB_USDC_LP)
    tryb_gauge = gauges[4]

    # get starting chain time
    chain.sleep(0)
    t0 = int(chain.time())

    # get the prior amount of rewards claimable for epoch
    base_dfx = tryb_gauge.claimable_reward(tester, addresses.DFX)
    base_usdc = tryb_gauge.claimable_reward(tester, addresses.USDC)
    lpt = tryb_gauge.balanceOf(tester)
    lpt_total = tryb_usdc_lpt.balanceOf(tryb_gauge)

    # fast-forward 24 hours
    chain.sleep(DAY)
    chain.mine()
    rewards_dfx = tryb_gauge.claimable_reward(tester, addresses.DFX)
    rewards_usdc = tryb_gauge.claimable_reward(tester, addresses.USDC)

    tryb_gauge.claim_rewards({"from": tester, "gas_price": gas_strategy})

    print(f"LPT in Gauge: {lpt / 1e18} (total: {lpt_total / 1e18})")
    print("LPT %:", lpt / lpt_total * 100)
    print("--- DFX")
    print("Past 24-hours rewards:", (rewards_dfx - base_dfx) / 1e18)
    print("--- USDC")
    print(base_usdc / 1e6, rewards_usdc / 1e6)
    print("Past 24-hours rewards:", (rewards_usdc - base_usdc) / 1e6)

    dfx = load_dfx_token()
    usdc = load_usdc_token()
    print(dfx.balanceOf(tester) / 1e18)
    print(usdc.balanceOf(tester) / 1e6)


if __name__ == "_main__":
    main()
