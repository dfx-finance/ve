#!/usr/bin/env python
import json
import time

from brownie import accounts

from scripts import contracts
from scripts.helper import get_addresses, gas_strategy, load_dfx_token

addresses = get_addresses()

DEPLOY_ACCT = accounts[0]

REWARDS_RATE = 1.9875488905e17
TOTAL_DFX_REWARDS = 5_118_750 * 1e18


output_data = {
    "distributor": {
        "proxy": None,
        "rewardsSupplied": None,
        "rewardsRate": None,
        "totalRewards": None,
    }
}


def send_dfx(dfx, amount, from_account, to_account):
    dfx.transfer(to_account, amount, {"from": from_account, "gas_price": gas_strategy})
    print("Sender account DFX balance:", dfx.balanceOf(from_account) / 1e18)


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. DfxDistributor address\n"
            "\t2. Total amount of rewards to provide\n"
            "\t3. New DFX token rewards per second\n"
        )
    )
    dfx = load_dfx_token()

    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    # provide multisig with ether
    DEPLOY_ACCT.transfer(addresses.DFX_MULTISIG, "2 ether", gas_price=gas_strategy)

    # Distribute rewards to the distributor contract
    send_dfx(dfx, TOTAL_DFX_REWARDS, addresses.DFX_MULTISIG, dfx_distributor)

    # Set rate to distribute 1,000,000 rewards (see spreadsheet)
    dfx_distributor.setRate(
        REWARDS_RATE, {"from": DEPLOY_ACCT, "gas_price": gas_strategy}
    )

    output_data["distributor"] = {
        "proxy": dfx_distributor.address,
        "rewardsSupplied": TOTAL_DFX_REWARDS,
        "rewardsRate": REWARDS_RATE,
        "totalRewards": dfx.balanceOf(dfx_distributor),
    }
    with open(f"./scripts/provided_rewards_{int(time.time())}.json", "w") as output_f:
        json.dump(output_data, output_f, indent=4)


if __name__ == "_main__":
    main()
