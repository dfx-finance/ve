#!/usr/bin/env python
from brownie import chain
from brownie import ChildChainFactory

from utils.ccip import ETHEREUM_CHAIN_SELECTOR
from utils.config import (
    DEPLOY_ACCT,
    DEPLOY_PROXY_ACCT,
    INSTANCE_ID,
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
            "\t1. LPT mainnet root gauge\n"
            "\t2. CCIP L2 Router\n"
            "\t3. Rewards-only Gauge Implementation\n"
            "\t4. LPT\n"
            "\t5. DFX multisig\n"
            "\t6. DFX token\n"
        )
    )

    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    factory = ChildChainFactory.at(deployed.read_addr("gaugeFactory"))

    # Polygon
    if chain.id == 137:
        # Deploy all contracts
        labels = ["cadcUsdc", "ngncUsdc", "trybUsdc", "xsgdUsdc", "usdceUsdc"]
        for label in labels:
            print((f"Deploying: {label} gauge set"))
            factory.deployGaugeSet(
                existing.read_addr(f"{label}RootGauge"),
                existing.read_addr("ccipRouter"),
                existing.read_addr("ccipSenderEth"),
                ETHEREUM_CHAIN_SELECTOR,
                deployed.read_addr("gaugeImplementation"),
                existing.read_addr(f"{label}Lpt"),
                existing.read_addr("multisig0"),
                DEPLOY_PROXY_ACCT,
                existing.read_addr("DFX"),
                {"from": DEPLOY_ACCT},
            )

            receiver, streamer, gauge = factory.gaugeSets(
                existing.read_addr(f"{label}RootGauge")
            )
            write_contract(INSTANCE_ID, f"{label}Receiver", receiver)
            write_contract(INSTANCE_ID, f"{label}Streamer", streamer)
            write_contract(INSTANCE_ID, f"{label}Gauge", gauge)

    # Arbitrum
    if chain.id == 42161:
        # Deploy all contracts
        labels = ["cadcUsdc", "gyenUsdc", "usdceUsdc"]
        for label in labels:
            print((f"Deploying: {label} gauge set"))
            factory.deployGaugeSet(
                existing.read_addr(f"{label}RootGauge"),
                existing.read_addr("ccipRouter"),
                existing.read_addr("ccipSenderEth"),
                ETHEREUM_CHAIN_SELECTOR,
                deployed.read_addr("gaugeImplementation"),
                existing.read_addr(f"{label}Lpt"),
                existing.read_addr("multisig0"),
                DEPLOY_PROXY_ACCT,
                existing.read_addr("DFX"),
                {"from": DEPLOY_ACCT},
            )
            receiver, streamer, gauge = factory.gaugeSets(
                existing.read_addr(f"{label}RootGauge")
            )
            write_contract(INSTANCE_ID, f"{label}Receiver", receiver)
            write_contract(INSTANCE_ID, f"{label}Streamer", streamer)
            write_contract(INSTANCE_ID, f"{label}Gauge", gauge)
