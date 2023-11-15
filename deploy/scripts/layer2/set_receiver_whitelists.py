#!/usr/bin/env python
from brownie import chain
from brownie import ChildChainReceiver

from utils.ccip import ETHEREUM_CHAIN_SELECTOR
from utils.config import (
    DEPLOY_ACCT,
    INSTANCE_ID,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs, write_contract
from utils.network import connected_network


existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


# whitelist root chain selector (ETH) and sender address
def whitelist_chain_and_sender(receiver_key: str) -> ChildChainReceiver:
    # print(f"--- Whitelist ETH chain selector on {connected_network} ---")
    receiver = ChildChainReceiver.at(deployed.read_addr(receiver_key))
    receiver.whitelistSourceChain(ETHEREUM_CHAIN_SELECTOR, {"from": DEPLOY_ACCT})
    # print(f"--- Whitelist ETH chain selector on {connected_network} ---")
    receiver.whitelistSender(existing.read_addr("ccipSenderEth"), {"from": DEPLOY_ACCT})


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. L2 gauge receiver address\n"
            "\t2. Mainnet sender contract\n"
        )
    )

    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    if chain.id == 137:
        whitelist_chain_and_sender("cadcUsdcReceiver")
        whitelist_chain_and_sender("ngncUsdcReceiver")
        whitelist_chain_and_sender("trybUsdcReceiver")
        whitelist_chain_and_sender("xsgdUsdcReceiver")
        whitelist_chain_and_sender("usdceUsdcReceiver")
    if chain.id == 42161:
        whitelist_chain_and_sender("cadcUsdcReceiver")
        whitelist_chain_and_sender("gyenUsdcReceiver")
        whitelist_chain_and_sender("usdceUsdcReceiver")
