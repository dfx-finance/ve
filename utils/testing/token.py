#!/usr/bin/env python
from brownie import accounts

from . import addresses
from ..chain import gas_strategy


def fund_multisig(account):
    account.transfer(addresses.DFX_MULTISIG, "10 ether", gas_price=gas_strategy)


def mint_dfx(dfx, amount, account):
    dfx.mint(
        account, amount, {"from": addresses.DFX_MULTISIG, "gas_price": gas_strategy}
    )


def mint_usdc(usdc, amount, account, deploy_account):
    usdc_owner = "0xfcb19e6a322b27c06842a71e8c725399f049ae3a"
    deploy_account.transfer(usdc_owner, "2 ether", gas_price=gas_strategy)

    usdc.updateMasterMinter(
        addresses.DFX_MULTISIG, {"from": usdc_owner, "gas_price": gas_strategy}
    )
    usdc.configureMinter(
        addresses.DFX_MULTISIG,
        amount,
        {"from": addresses.DFX_MULTISIG, "gas_price": gas_strategy},
    )
    usdc.mint(
        account,
        amount,
        {
            "from": addresses.DFX_MULTISIG,
            "gas_price": gas_strategy,
        },
    )
