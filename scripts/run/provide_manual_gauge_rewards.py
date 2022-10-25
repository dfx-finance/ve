#!/usr/bin/env python
from brownie import accounts

from scripts import contracts
from scripts.helper import get_addresses, gas_strategy, load_dfx_token, DEPLOY_ACCT


addresses = get_addresses()

DFX_MULTISIG = accounts.at(address=addresses.DFX_MULTISIG, force=True)
TOPUP_DFX_REWARDS = 8586.21120696 * 1e18


def send_dfx(dfx, amount, from_account, to_account):
    dfx.transfer(to_account, amount, {
                 'from': from_account, 'gas_price': gas_strategy})
    print('Sender account DFX balance:',
          dfx.balanceOf(from_account) / 1e18)

def main():
    print((
        'NOTE: This script expects configuration for:\n'
        '\t1. DfxDistributor address\n'
    ))
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)
    dfx = load_dfx_token()

    # provide multisig with ether
    DEPLOY_ACCT.transfer(addresses.DFX_MULTISIG,
                         "2 ether", gas_price=gas_strategy)

    # Distribute rewards to the distributor contract
    dfx.approve(dfx_distributor, 1_000_000_000 * 1e18, {'from': DFX_MULTISIG, 'gas_price': gas_strategy})
    for gauge in contracts.gauges():
        dfx_distributor.passRewardToGauge(gauge, dfx, TOPUP_DFX_REWARDS,
            {'from': DFX_MULTISIG, 'gas_price': gas_strategy})


if __name__ == '_main__':
    main()
