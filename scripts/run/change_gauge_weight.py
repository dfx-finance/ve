#!/usr/bin/env python
from brownie import accounts

from scripts import contracts
from scripts.helper import get_addresses, gas_strategy

DEPLOY_ACCT = accounts[0]


addresses = get_addresses()

# Gauges whose weights should be set to 0
orig_gauges = [
    "0x85aD6DCfd14696da299e6a5097DFEf0ACEaE902d",
    "0xB48cCFcE88E7E321E4A582b62844d814Cf092aD1",
    "0x2C7275dC37Dd9799776A7d8a121dF338738D0bEe",
    "0x32b1E7Ca34D1c1A28701ce731B4d2845152197b7",
    "0x3Bc9016eC6dAac5ac474De1ae3BfDC3c28e724Bf",
    "0x31696BdbcD03fB06b1F62DD0DEDe9b25AF2F3160",
    "0x7FFE7048e468b3bf08fD6F6998E34F44883f1923",
]


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. DfxDistributor address\n"
        )
    )

    # provide multisig with ether
    DEPLOY_ACCT.transfer(addresses.DFX_MULTISIG, "2 ether", gas_price=gas_strategy)
    DFX_MULTISIG = accounts.at(address=addresses.DFX_MULTISIG, force=True)

    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)
    for gauge_addr in orig_gauges:
        gauge_controller.change_gauge_weight(
            gauge_addr, 0, {"from": DFX_MULTISIG, "gas_price": gas_strategy}
        )


if __name__ == "_main__":
    main()
