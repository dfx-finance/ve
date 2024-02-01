#!/usr/bin/env python
from brownie import chain
from brownie import ChildChainReceiver

from utils.config import (
    DEPLOY_ACCT,
    INSTANCE_ID,
    VERIFY_CONTRACTS,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs, write_contract
from utils.network import connected_network

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. CCIP Router address\n"
            "\t2. Existing L2 gauge sets"
        )
    )

    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    # Polygon
    if chain.id == 137:
        pairs = [
            "cadcUsdc",
            "ngncUsdc",
            "paxgUsdc",
            "trybUsdc",
            "xsgdUsdc",
            "usdceUsdc",
        ]
        for label in pairs:
            receiver = ChildChainReceiver.deploy(
                existing.read_addr("ccipRouter"),
                deployed.read_addr(f"{label}Streamer"),
                DEPLOY_ACCT,
                {"from": DEPLOY_ACCT},
                publish_source=VERIFY_CONTRACTS,
            )
            receiver.whitelistSourceChain(
                existing.read_addr("chainSelectorEth"), {"from": DEPLOY_ACCT}
            )
            receiver.whitelistSender(
                existing.read_addr("ccipSenderEth"), {"from": DEPLOY_ACCT}
            )
            receiver.setOwner(existing.read_addr("multisig0"), {"from": DEPLOY_ACCT})
            write_contract(INSTANCE_ID, f"{label}Receiver", receiver)
            break

    # Arbitrum
    if chain.id == 42161:
        pairs = ["cadcUsdc", "gyenUsdc", "usdceUsdc"]
        for label in pairs:
            receiver = ChildChainReceiver.deploy(
                existing.read_addr("ccipRouter"),
                deployed.read_addr(f"{label}Streamer"),
                DEPLOY_ACCT,
                {"from": DEPLOY_ACCT},
                publish_source=VERIFY_CONTRACTS,
            )
            receiver.whitelistSourceChain(
                existing.read_addr("chainSelectorEth"), {"from": DEPLOY_ACCT}
            )
            receiver.whitelistSender(
                existing.read_addr("ccipSenderEth"), {"from": DEPLOY_ACCT}
            )
            receiver.setOwner(existing.read_addr("multisig0"), {"from": DEPLOY_ACCT})
            write_contract(INSTANCE_ID, f"{label}Receiver", receiver)
