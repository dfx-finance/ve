#!/usr/bin/env python
from brownie import RewardsOnlyGaugeUpgrade

from utils.config import (
    DEPLOY_ACCT,
    DEPLOY_PROXY_ACCT,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.network import connected_network


def deploy_implementation() -> RewardsOnlyGaugeUpgrade:
    print(f"--- Deploying Root Gauge CCIP contract to {connected_network} ---")
    gauge_logic = RewardsOnlyGaugeUpgrade.deploy({"from": DEPLOY_ACCT})
    return gauge_logic


def main():
    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    gauge_logic = deploy_implementation()
