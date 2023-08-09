#!/usr/bin/env python
# 1. Stop distribution to all gauges
#    - Rewards within gauge will remain available to _any_ user who continues to stake through following epoch
# 2. Withdraw all DFX ERC20 from distributor gauge to multisig
from brownie.network import gas_price

from fork.utils.account import DEPLOY_ACCT, impersonate
from utils import contracts
from utils.gas import gas_strategy
from utils.helper import fund_multisigs
from utils.network import get_network_addresses


gas_price(gas_strategy)
addresses = get_network_addresses()


def main():
    fund_multisigs(DEPLOY_ACCT)
    admin = impersonate(addresses.DFX_MULTISIG_0)

    dfx = contracts.load_dfx_token()
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    # disable distributions
    dfx_distributor.toggleDistributions({"from": admin, "gas_price": gas_strategy})

    # set rate to 0
    dfx_distributor.setRate(0, {"from": admin, "gas_price": gas_strategy})

    distributor_bal = dfx.balanceOf(dfx_distributor.address)
    multisig_starting_bal = dfx.balanceOf(admin)
    dfx_distributor.recoverERC20(
        dfx.address,
        admin,
        distributor_bal,
        {"from": admin, "gas_price": gas_strategy},
    )
    multisig_ending_bal = dfx.balanceOf(admin)
    print(
        "DFX rewards recovered:", (multisig_ending_bal - multisig_starting_bal) / 1e18
    )


if __name__ == "__main__":
    pass
