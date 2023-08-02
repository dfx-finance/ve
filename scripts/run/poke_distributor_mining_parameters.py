#!/usr/bin/env python
from utils import contracts
from utils.account import DEPLOY_ACCT
from utils.gas import gas_strategy
from utils.network import get_network_addresses


addresses = get_network_addresses()


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. DfxDistributor address\n"
        )
    )
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    # Public function to advance epoch & recalculate reward rate when previous
    # epoch has expired
    # NOTE: returns a "108" error when rate has been updated for this epoch,
    # either via this function or `distributeReward/distributorRewardToMultipleGauges`
    dfx_distributor.updateMiningParameters(
        {"from": DEPLOY_ACCT, "gas_price": gas_strategy}
    )


if __name__ == "_main__":
    main()
