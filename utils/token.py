#!/usr/bin/env python
from brownie.network.gas.strategies import LinearScalingStrategy

from . import addresses


# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('30 gwei', '250 gwei', 1.3)


def fund_multisig(account):
    account.transfer(addresses.DFX_MULTISIG,
                     '10 ether',
                     gas_price=gas_strategy)


def mint_dfx(dfx, amount, account):
    dfx.mint(account, amount,
             {'from': addresses.DFX_MULTISIG, 'gas_price': gas_strategy})


def send_dfx(dfx, amount, from_account, to_account):
    dfx.transfer(to_account, amount, {
                 'from': from_account, 'gas_price': gas_strategy})


def assert_tokens_balance(tokens, account, amount):
    for token in tokens:
        balance = token.balanceOf(account) / 10 ** token.decimals()
        assert balance == amount
