#!/usr/bin/env python
from . import addresses
from ..chain import gas_strategy

def fund_multisig(account):
    account.transfer(addresses.DFX_MULTISIG,
                     '10 ether',
                     gas_price=gas_strategy)


def mint_dfx(dfx, amount, account):
    dfx.mint(account, amount,
             {'from': addresses.DFX_MULTISIG, 'gas_price': gas_strategy})