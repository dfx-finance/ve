#!/usr/bin/env python
import json
import time

from brownie import (
    RewardsOnlyGauge,
    DfxUpgradeableProxy,
    ChildChainStreamer,
    ChildChainReceiver,
    Contract,
    ZERO_ADDRESS,
)

from fork.utils.account import DEPLOY_ACCT, DEPLOY_PROXY_ACCT
from utils.constants_addresses import Arbitrum
from utils.helper import verify_deploy_address, verify_deploy_network
from utils.log import write_contract
from utils.network import network_info

connected = network_info()

output_data = {
    "gaugeImplementation": None,
    "gauges": {},
}
output_data_gauge = {
    "lpt": None,
    "receiver": None,
    "streamer": None,
    "gaugeImplementation": None,
    "gaugeProxy": None,
}


# deploy l2 rewards-only gauge
def deploy_gauge_implementation() -> RewardsOnlyGauge:
    print(f"--- Deploying L2 gauge implementation contract to {connected.name} ---")
    gauge_logic = RewardsOnlyGauge.deploy(
        {"from": DEPLOY_ACCT},
    )
    output_data["gaugeImplementation"] = gauge_logic.address
    return gauge_logic


# deploy gauge proxy and initialize
def deploy_gauge(
    gauge_logic: RewardsOnlyGauge, lpt_addr: str, label: str, verify_contracts=False
) -> RewardsOnlyGauge:
    print(f"--- Deploying L2 gauge proxy contract to {connected.name} ---")
    gauge_initializer_calldata = gauge_logic.initialize.encode_input(
        DEPLOY_ACCT, lpt_addr
    )
    proxy = DfxUpgradeableProxy.deploy(
        gauge_logic.address,
        DEPLOY_PROXY_ACCT,
        gauge_initializer_calldata,
        {"from": DEPLOY_ACCT},
        publish_source=verify_contracts,
    )
    gauge = Contract.from_abi("RewardsOnlyGauge", proxy, RewardsOnlyGauge.abi)
    output_data["gauges"].setdefault(label, output_data_gauge)
    output_data["gauges"][label]["gaugeProxy"] = gauge.address
    write_contract(f"{label}ArbitrumGauge", gauge.address)
    return gauge


# deploy childchainstreamer
def deploy_streamer(gauge: RewardsOnlyGauge, label: str) -> ChildChainStreamer:
    print(f"--- Deploying ChildChainStreamer contract to {connected.name} ---")
    streamer = ChildChainStreamer.deploy(
        DEPLOY_ACCT,
        gauge,
        Arbitrum.CCIP_DFX,
        {"from": DEPLOY_ACCT},
    )
    output_data["gauges"][label]["streamer"] = streamer.address
    write_contract(f"{label}ArbitrumStreamer", streamer.address)
    return streamer


# deploy childchainreceiver
def deploy_receiver(
    streamer: ChildChainStreamer, label: str, verify_contracts=False
) -> ChildChainReceiver:
    print(f"--- Deploying Receiver contract to {connected.name} ---")
    receiver = ChildChainReceiver.deploy(
        Arbitrum.CCIP_ROUTER,
        streamer,
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT},
        publish_source=verify_contracts,
    )
    output_data["gauges"][label]["receiver"] = receiver.address
    write_contract(f"{label}ArbitrumReceiver", receiver.address)
    return receiver


# grouped deployment of all contracts for an LP pair
def deploy_contract_set(
    gauge_logic: RewardsOnlyGauge, lpt_addr: str, label: str, verify: bool
):
    gauge = deploy_gauge(gauge_logic, lpt_addr, label, verify)
    streamer = deploy_streamer(gauge, label)
    receiver = deploy_receiver(streamer, label, verify)
    return receiver, streamer, gauge


def configure(receiver, streamer, gauge):
    print(
        f"--- Configuring ChildChainStreamer contract with ChildChainReceiver as reward distributor ---"
    )
    # update authorized user for childchainstreamer rewards
    # DEV: This will be the address of the CCTP contract which is calling "notify_reward_amount"
    # on ChildChainStreamer
    streamer.set_reward_distributor(
        Arbitrum.CCIP_DFX, receiver.address, {"from": DEPLOY_ACCT}
    )

    print(f"--- Configuring RewardsOnlyGauge contract with DFX rewards ---")
    # set rewards contract on gauge
    # DEV: cannot be set while gauge has 0 deposits?
    gauge.set_rewards(
        streamer,
        streamer.signatures["get_reward"],
        [
            Arbitrum.CCIP_DFX,
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

    verify_deploy_network(connected.name)
    verify_deploy_address(DEPLOY_ACCT)

    gauge_logic = deploy_gauge_implementation()

    # Deploy all contracts
    verify_contracts = False if connected.is_local else True
    cadc_usdc_receiver, cadc_usdc_streamer, cadc_usdc_gauge = deploy_contract_set(
        gauge_logic, Arbitrum.DFX_CADC_USDC_LP, "cadcUsdc", verify_contracts
    )
    gyen_usdc_receiver, gyen_usdc_streamer, gyen_usdc_gauge = deploy_contract_set(
        gauge_logic, Arbitrum.DFX_GYEN_USDC_LP, "gyenUsdc", verify_contracts
    )

    # Configure ChildChainStreamer distributor address (router), gauge
    # reward token address (ccDFX on L2), and whitelisting on ChildChainReceiver
    configure(cadc_usdc_receiver, cadc_usdc_streamer, cadc_usdc_gauge)
    configure(gyen_usdc_receiver, gyen_usdc_streamer, gyen_usdc_gauge)

    # Write output to file
    if not connected.is_local:
        with open(
            f"./scripts/arbitrum_l2_gauges_{int(time.time())}.json", "w"
        ) as output_f:
            json.dump(output_data, output_f, indent=4)
