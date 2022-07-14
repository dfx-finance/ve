#!/usr/bin/env python
import brownie
from brownie.network.gas.strategies import LinearScalingStrategy

import addresses

WEEK = 86400 * 7

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('30 gwei', '250 gwei', 1.3)


# Advance chain clock
def fastforward_chain(seconds):
    brownie.chain.sleep(seconds)
    brownie.chain.mine()


def fund_multisig(account):
    account.transfer(addresses.DFX_MULTISIG,
                     '10 ether',
                     gas_price=gas_strategy)


def mint_dfx(dfx, amount, account):
    print("Account DFX balance (pre-mint):",
          dfx.balanceOf(account) / 1e18)
    dfx.mint(account, amount,
             {'from': addresses.DFX_MULTISIG, 'gas_price': gas_strategy})
    print("Account DFX balance (post-mint):",
          dfx.balanceOf(account) / 1e18)


def send_dfx(dfx, amount, from_account, to_account):
    dfx.transfer(to_account, amount, {
                 'from': from_account, 'gas_price': gas_strategy})
    print("Sender account DFX balance:",
          dfx.balanceOf(from_account) / 1e18)


def assert_tokens_balance(tokens, account, amount):
    for token in tokens:
        balance = token.balanceOf(account) / 10 ** token.decimals()
        assert balance == amount
