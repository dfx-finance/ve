#!/usr/bin/env python
from dotenv import load_dotenv
import sys

from .gas import gas_strategy

load_dotenv()


def fund_multisigs(funder, multisig_accounts):
    for multisig_account in multisig_accounts:
        funder.transfer(multisig_account, "10 ether", gas_price=gas_strategy)


def mint_dfx(dfx, amount, account, master_account):
    dfx.mint(account, amount, {"from": master_account, "gas_price": gas_strategy})


def send_dfx(dfx, amount, from_account, to_account):
    dfx.transfer(to_account, amount, {"from": from_account, "gas_price": gas_strategy})


def assert_tokens_balance(tokens, account, amount):
    for token in tokens:
        balance = token.balanceOf(account) / 10 ** token.decimals()
        assert balance == amount


def verify_deploy_address(address):
    print(f"Using deploy address: {address}")
    if not input("Confirm? (y/n)  ").lower().strip() == "y":
        print("Canceled")
        sys.exit(1)


def verify_deploy_network(network):
    print(f"Deploying on network: {network}")
    if not input("Confirm? (y/n)  ").lower().strip() == "y":
        print("Canceled")
        sys.exit(1)


def verify_gas_strategy():
    print(
        f"Gas range: {int(gas_strategy.initial_gas_price / 1e9)} -> {int(gas_strategy.max_gas_price / 1e9)}"
    )
    if not input("Confirm? (y/n)  ").lower().strip() == "y":
        print("Canceled")
        sys.exit(1)
    print("Gas strategy verified!")
