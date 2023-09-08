#!/usr/bin/env python
from brownie import CCIPDemo

from utils.network import get_network_addresses, network_info
from ..utils_ccip import DEPLOY_ACCT

addresses = get_network_addresses()
connected_network, is_local_network = network_info()


def deploy():
    demo = CCIPDemo.deploy(
        addresses.CCIP_ROUTER,
        {"from": DEPLOY_ACCT},
        publish_source=True,
    )
    return demo


def main():
    # Deploy all contracts
    demo = deploy()

    print(f"Demo: {demo.address}")
