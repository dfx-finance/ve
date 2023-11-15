#!/usr/bin/env python
from brownie import chain, Contract, ZERO_ADDRESS
from brownie import (
    RewardsOnlyGauge,
    DfxUpgradeableProxy,
    ChildChainStreamer,
    ChildChainReceiver,
)
import time

from utils.config import (
    DEPLOY_ACCT,
    DEPLOY_PROXY_ACCT,
    INSTANCE_ID,
    VERIFY_CONTRACTS,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs, write_contract
from utils.network import connected_network, is_localhost

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


# deploy l2 rewards-only gauge
def deploy_gauge_implementation() -> RewardsOnlyGauge:
    print(f"--- Deploying L2 gauge implementation contract to {connected_network} ---")
    gauge_logic = RewardsOnlyGauge.deploy(
        {"from": DEPLOY_ACCT}, publish_source=VERIFY_CONTRACTS
    )
    write_contract(INSTANCE_ID, "gaugeImplementation", gauge_logic.address)
    return gauge_logic


def load_gauge_implementation() -> RewardsOnlyGauge:
    print(f"--- Loading Rewards Gauge CCIP contract on {connected_network} ---")
    gauge_logic = RewardsOnlyGauge.at(deployed.read_addr("gaugeImplementation"))
    return gauge_logic


# deploy gauge proxy and initialize
def deploy_gauge(gauge_logic: RewardsOnlyGauge, label: str) -> RewardsOnlyGauge:
    _label = f"{label}Gauge"
    if deployed.get(_label):
        return Contract.from_abi(
            "RewardsOnlyGauge", deployed.read_addr(_label), RewardsOnlyGauge.abi
        )

    lpt = existing.read_addr(f"{label}Lpt")

    print(f"--- Deploying L2 gauge proxy contract to {connected_network} ---")
    gauge_initializer_calldata = gauge_logic.initialize.encode_input(DEPLOY_ACCT, lpt)
    proxy = DfxUpgradeableProxy.deploy(
        gauge_logic.address,
        DEPLOY_PROXY_ACCT,
        gauge_initializer_calldata,
        {"from": DEPLOY_ACCT},
    )
    gauge = Contract.from_abi("RewardsOnlyGauge", proxy, RewardsOnlyGauge.abi)
    write_contract(INSTANCE_ID, _label, gauge.address)
    return gauge


# deploy childchainstreamer
def deploy_streamer(gauge: RewardsOnlyGauge, label: str) -> ChildChainStreamer:
    _label = f"{label}Streamer"
    if deployed.get(_label):
        return ChildChainStreamer.at(deployed.read_addr(_label))

    print(f"--- Deploying ChildChainStreamer contract to {connected_network} ---")
    streamer = ChildChainStreamer.deploy(
        DEPLOY_ACCT,
        gauge,
        existing.read_addr("DFX"),
        {"from": DEPLOY_ACCT},
    )
    write_contract(INSTANCE_ID, _label, streamer.address)
    return streamer


# deploy childchainreceiver
def deploy_receiver(streamer: ChildChainStreamer, label: str) -> ChildChainReceiver:
    _label = f"{label}Receiver"
    if deployed.get(_label):
        return ChildChainReceiver.at(deployed.read_addr(_label))

    print(f"--- Deploying Receiver contract to {connected_network} ---")
    receiver = ChildChainReceiver.deploy(
        existing.read_addr("ccipRouter"),
        streamer,
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )
    write_contract(INSTANCE_ID, _label, receiver.address)
    return receiver


# grouped deployment of all contracts for an LP pair
def deploy_contract_set(gauge_logic: RewardsOnlyGauge, label: str):
    gauge = deploy_gauge(gauge_logic, label)
    streamer = deploy_streamer(gauge, label)
    deploy_receiver(streamer, label)


def configure(receiver_key: str, streamer_key: str, gauge_key: str):
    print(
        f"--- Configuring ChildChainStreamer contract with ChildChainReceiver as reward distributor ---"
    )

    receiver = ChildChainReceiver.at(deployed.read_addr(receiver_key))
    streamer = ChildChainStreamer.at(deployed.read_addr(streamer_key))
    gauge = Contract.from_abi(
        "RewardsOnlyGauge", deployed.read_addr(gauge_key), RewardsOnlyGauge.abi
    )

    # update authorized user for childchainstreamer rewards
    # DEV: This will be the address of the CCTP contract which is calling "notify_reward_amount"
    # on ChildChainStreamer
    streamer.set_reward_distributor(
        existing.read_addr("DFX"), receiver.address, {"from": DEPLOY_ACCT}
    )

    print(f"--- Configuring RewardsOnlyGauge contract with DFX rewards ---")
    # set rewards contract on gauge
    # DEV: cannot be set while gauge has 0 deposits?
    gauge.set_rewards(
        streamer,
        streamer.signatures["get_reward"],
        [
            existing.read_addr("DFX"),
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
        ],
        {"from": DEPLOY_ACCT},
    )


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. CCIP Router address\n"
            "\t2. Reward token address\n"
        )
    )

    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    # gauge_logic = deploy_gauge_implementation()
    # if not is_localhost:
    #     print("Sleeping after deploy....")
    #     time.sleep(3)
    gauge_logic = load_gauge_implementation()

    # Polygon
    if chain.id == 137:
        # Deploy all contracts
        labels = ["cadcUsdc", "ngncUsdc", "trybUsdc", "xsgdUsdc", "usdceUsdc"]
        for label in labels:
            print((f"Deploying: {label}"))
            deploy_contract_set(gauge_logic, label)

        # Configure ChildChainStreamer distributor address (router), gauge
        # reward token address (clDFX on L2), and whitelisting on ChildChainReceiver
        json_keys = [
            ["cadcUsdcReceiver", "cadcUsdcStreamer", "cadcUsdcGauge"],
            ["ngncUsdcReceiver", "ngncUsdcStreamer", "ngncUsdcGauge"],
            ["trybUsdcReceiver", "trybUsdcStreamer", "trybUsdcGauge"],
            ["xsgdUsdcReceiver", "xsgdUsdcStreamer", "xsgdUsdcGauge"],
            ["usdceUsdcReceiver", "usdceUsdcStreamer", "uscdeUsdcGauge"],
        ]
        for receiver_key, streamer_key, gauge_key in json_keys:
            print((f"Configuring: {receiver_key}, {streamer_key}, {gauge_key}"))
            configure(receiver_key, streamer_key, gauge_key)

    # Arbitrum
    if chain.id == 42161:
        # Deploy all contracts
        labels = ["cadcUsdc", "gyenUsdc", "usdceUsdc"]
        for label in labels:
            print((f"Deploying: {label}"))
            deploy_contract_set(gauge_logic, label)

        # Configure ChildChainStreamer distributor address (router), gauge
        # reward token address (clDFX on L2), and whitelisting on ChildChainReceiver
        json_keys = [
            ["cadcUsdcReceiver", "cadcUsdcStreamer", "cadcUsdcGauge"],
            ["gyenUsdcReceiver", "gyenUsdcStreamer", "gyenUsdcGauge"],
            ["usdceUsdcReceiver", "usdceUsdcStreamer", "usdceUsdcGauge"],
        ]
        for receiver_key, streamer_key, gauge_key in json_keys:
            print((f"Configuring: {receiver_key}, {streamer_key}, {gauge_key}"))
            configure(receiver_key, streamer_key, gauge_key)
