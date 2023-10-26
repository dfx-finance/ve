#!/usr/bin/env python
from brownie import (
    RewardsOnlyGauge,
    DfxUpgradeableProxy,
    ChildChainStreamer,
    ChildChainReceiver,
    Contract,
    ZERO_ADDRESS,
)

from utils.config import (
    DEPLOY_ACCT,
    DEPLOY_PROXY_ACCT,
    INSTANCE_ID,
    VERIFY_CONTRACTS,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs, write_contract
from utils.network import connected_network

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


# deploy l2 rewards-only gauge
def deploy_gauge_implementation() -> RewardsOnlyGauge:
    print(f"--- Deploying L2 gauge implementation contract to {connected_network} ---")
    gauge_logic = RewardsOnlyGauge.deploy(
        {"from": DEPLOY_ACCT},
    )
    write_contract(INSTANCE_ID, "gaugeImplementation", gauge_logic.address)
    return gauge_logic


# deploy gauge proxy and initialize
def deploy_gauge(gauge_logic: RewardsOnlyGauge, label: str) -> RewardsOnlyGauge:
    lpt = existing.read_addr(f"{label}Lp")

    print(f"--- Deploying L2 gauge proxy contract to {connected_network} ---")
    gauge_initializer_calldata = gauge_logic.initialize.encode_input(
        DEPLOY_ACCT,
        lpt,
    )
    proxy = DfxUpgradeableProxy.deploy(
        gauge_logic.address,
        DEPLOY_PROXY_ACCT,
        gauge_initializer_calldata,
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )
    gauge = Contract.from_abi("RewardsOnlyGauge", proxy, RewardsOnlyGauge.abi)
    write_contract(
        INSTANCE_ID, f"arbitrum{label[0].upper() + label[1:]}Gauge", gauge.address
    )
    return gauge


# deploy childchainstreamer
def deploy_streamer(gauge: RewardsOnlyGauge, label: str) -> ChildChainStreamer:
    print(f"--- Deploying ChildChainStreamer contract to {connected_network} ---")
    streamer = ChildChainStreamer.deploy(
        DEPLOY_ACCT,
        gauge,
        deployed.read_addr("clDFX"),
        {"from": DEPLOY_ACCT},
    )
    _label = label[0].upper() + label[1:]  # capitalize first letter, others unchanged
    write_contract(f"arbitrum{_label}Streamer", streamer.address)
    return streamer


# deploy childchainreceiver
def deploy_receiver(streamer: ChildChainStreamer, label: str) -> ChildChainReceiver:
    print(f"--- Deploying Receiver contract to {connected_network} ---")
    receiver = ChildChainReceiver.deploy(
        existing.read_addr("ccipRouter"),
        streamer,
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )
    _label = label[0].upper() + label[1:]  # capitalize first letter, others unchanged
    write_contract(f"arbitrum{_label}Receiver", receiver.address)
    return receiver


# grouped deployment of all contracts for an LP pair
def deploy_contract_set(gauge_logic: RewardsOnlyGauge, lpt_addr: str, label: str):
    gauge = deploy_gauge(gauge_logic, lpt_addr, label)
    streamer = deploy_streamer(gauge, label)
    receiver = deploy_receiver(streamer, label)
    return receiver, streamer, gauge


def configure(receiver, streamer, gauge):
    print(
        f"--- Configuring ChildChainStreamer contract with ChildChainReceiver as reward distributor ---"
    )
    # update authorized user for childchainstreamer rewards
    # DEV: This will be the address of the CCTP contract which is calling "notify_reward_amount"
    # on ChildChainStreamer
    streamer.set_reward_distributor(
        deployed.read_addr("clDFX"), receiver.address, {"from": DEPLOY_ACCT}
    )

    print(f"--- Configuring RewardsOnlyGauge contract with DFX rewards ---")
    # set rewards contract on gauge
    # DEV: cannot be set while gauge has 0 deposits?
    gauge.set_rewards(
        streamer,
        streamer.signatures["get_reward"],
        [
            deployed.read_addr("clDFX"),
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

    gauge_logic = deploy_gauge_implementation()

    # Deploy all contracts
    cadc_usdc_receiver, cadc_usdc_streamer, cadc_usdc_gauge = deploy_contract_set(
        gauge_logic, "cadcUsdc"
    )
    gyen_usdc_receiver, gyen_usdc_streamer, gyen_usdc_gauge = deploy_contract_set(
        gauge_logic, "gyenUsdc"
    )

    # Configure ChildChainStreamer distributor address (router), gauge
    # reward token address (clDFX on L2), and whitelisting on ChildChainReceiver
    configure(cadc_usdc_receiver, cadc_usdc_streamer, cadc_usdc_gauge)
    configure(gyen_usdc_receiver, gyen_usdc_streamer, gyen_usdc_gauge)
