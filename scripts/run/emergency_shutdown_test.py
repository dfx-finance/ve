#!/usr/bin/env python
# 1. Stop distribution to all gauges
#    - Rewards within gauge will remain available to _any_ user who continues to stake through following epoch
# 2. Withdraw all DFX ERC20 from distributor gauge to multisig
from brownie import accounts
from brownie.network import gas_price

from scripts import contracts
from scripts.helper import gas_strategy, get_addresses, load_dfx_token, DEPLOY_ACCT


gas_price(gas_strategy)
addresses = get_addresses()

DFX_MULTISIG = accounts.at(address=addresses.DFX_MULTISIG, force=True)

RETURN_ADDR = "0x9715C357cC02a60906E137608f95ca0148f438e7"

def main():
    dfx = load_dfx_token()
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    distributor_bal = dfx.balanceOf(dfx_distributor.address)
    multisig_starting_bal = dfx.balanceOf(RETURN_ADDR)
    dfx_distributor.recoverERC20(dfx.address, RETURN_ADDR, distributor_bal, {
                                 'from': DEPLOY_ACCT, 'gas_price': gas_strategy})
    multisig_ending_bal = dfx.balanceOf(RETURN_ADDR)
    print(multisig_starting_bal)
    print(multisig_ending_bal)


if __name__ == '__main__':
    pass
