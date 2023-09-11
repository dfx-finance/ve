#!/usr/bin/env python
from brownie import ChildChainStreamer, ChildChainReceiver

from utils.constants_addresses import Sepolia
from utils.network import get_network_addresses, network_info
from ..utils_ccip import DEPLOY_ACCT, SEPOLIA_CHAIN_SELECTOR

addresses = get_network_addresses()
connected_network, is_local_network = network_info()


def deploy(streamer):
    # deploy childchainreceiver
    receiver = ChildChainReceiver.deploy(
        addresses.CCIP_ROUTER,
        streamer,
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT},
        publish_source=True,
    )

    return receiver


def configure(receiver, streamer):
    # update authorized user for childchainstreamer rewards
    # DEV: This will be the address of the CCTP contract which is calling "notify_reward_amount"
    # on ChildChainStreamer
    streamer.set_reward_distributor(
        addresses.CCIP_DFX, receiver.address, {"from": DEPLOY_ACCT}
    )

    # whitelist source chain and address on receiver
    receiver.whitelistSourceChain(SEPOLIA_CHAIN_SELECTOR, {"from": DEPLOY_ACCT})
    receiver.whitelistSender(Sepolia.MUMBAI_ETH_BTC_ROOT_GAUGE, {"from": DEPLOY_ACCT})


def load():
    streamer = ChildChainStreamer.at(addresses.CCIP_STREAMER)
    return streamer


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. CCIP Router address\n"
            "\t2. Reward token address\n"
        )
    )

    # Load and deploy contracts
    streamer = load()
    receiver = deploy(streamer)

    # Configure ChildChainStreamer distributor address (router) and whitelisting on ChildChainReceiver
    configure(receiver, streamer)

    print(f"Streamer: {streamer.address}")
    print(f"Receiver: {receiver.address}")
