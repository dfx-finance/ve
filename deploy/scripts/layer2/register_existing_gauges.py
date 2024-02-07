#!/usr/bin/env python
from brownie import ChildChainRegistry
from brownie import chain, ZERO_ADDRESS

from utils.config import (
    DEPLOY_ACCT,
    DEPLOY_PROXY_ACCT,
    INSTANCE_ID,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)
deployed_mainnet = load_outputs(INSTANCE_ID, chain_id=1)


def register_gauge(network_name, label):
    # registry = ChildChainRegistry.at(deployed.read_addr("gaugeRegistry"))
    registry = ChildChainRegistry.at("0x998814004f9d6AE314ec359B6B5149cD872A98b7")

    root_gauge_label = label[0].upper() + label[1:]
    root_gauge = deployed_mainnet.read_addr(
        f"{network_name}{root_gauge_label}RootGauge"
    )

    if registry.gaugeSets(root_gauge)["childGauge"] == ZERO_ADDRESS:
        print(f"Register: {label} gauge set")
        receiver = deployed.read_addr(f"{label}Receiver")
        streamer = deployed.read_addr(f"{label}Streamer")
        child_gauge = deployed.read_addr(f"{label}Gauge")
        registry.registerGaugeSet(
            root_gauge, receiver, streamer, child_gauge, {"from": DEPLOY_ACCT}
        )
    else:
        print(f"Exists in registry: {label} gauge set")


def main():
    if chain.id == 137:
        labels = [
            "cadcUsdc",
            "ngncUsdc",
            "paxgUsdc",
            "trybUsdc",
            "xsgdUsdc",
            "usdceUsdc",
        ]
        for label in labels:
            register_gauge("polygon", label)
    if chain.id == 42161:
        labels = ["cadcUsdc", "gyenUsdc", "usdceUsdc"]
        for label in labels:
            register_gauge("arbitrum", label)
