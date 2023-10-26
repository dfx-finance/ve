#!/usr/bin/env python
from brownie import accounts, network, web3
from brownie.network.gas.strategies import LinearScalingStrategy
import dotenv
import os
import sys

from .network import is_localhost

# load .env variables
dotenv.load_dotenv()

# globals
INSTANCE_ID = os.getenv("INSTANCE_ID", "primary")
DEPLOY_ACCT = accounts[0] if is_localhost else accounts.load("deploy-ve-test")
DEFAULT_GAUGE_TYPE = 0
DEFAULT_GAUGE_WEIGHT = 1e18

# gas -- set default scaling gas price for all transactions
current_gas_price = web3.eth.gas_price
gas_strategy = LinearScalingStrategy(
    current_gas_price,
    current_gas_price + 20,
    increment=1.05,
)
network.gas_price(gas_strategy)


# guards before run
def verify_deploy_address(address):
    print(f"Using deploy address: {address}")
    if input("Confirm? (y/n)  ").lower().strip() not in ["y", "yes"]:
        print("Canceled")
        sys.exit(1)


def verify_deploy_network(network):
    print(f"Deploying on network: {network}")
    if input("Confirm? (y/n)  ").lower().strip() not in ["y", "yes"]:
        print("Canceled")
        sys.exit(1)
