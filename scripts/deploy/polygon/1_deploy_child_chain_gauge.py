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
from utils.constants_addresses import Polygon
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
def deploy_gauge_implementation(verify_contracts=False) -> RewardsOnlyGauge:
    print(f"--- Deploying L2 gauge implementation contract to {connected.name} ---")
    gauge_logic = RewardsOnlyGauge.deploy(
        {"from": DEPLOY_ACCT},
        publish_source=verify_contracts,
    )
    output_data["gaugeImplementation"] = gauge_logic.address
    return gauge_logic


def load_gauge_implementation() -> RewardsOnlyGauge:
    print(f"--- Loading Rewards Gauge CCIP contract on {connected.name} ---")
    gauge_logic = RewardsOnlyGauge.at(Polygon.GAUGE_IMPLEMENTATION)
    return gauge_logic


# deploy gauge proxy and initialize
def deploy_gauge(
    gauge_logic: RewardsOnlyGauge,
    lpt_addr: str,
    label: str,
    verify_contracts=False,
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
    write_contract(f"polygon{label[0].upper() + label[1:]}Gauge", gauge.address)
    return gauge


# deploy childchainstreamer
def deploy_streamer(gauge: RewardsOnlyGauge, label: str) -> ChildChainStreamer:
    print(f"--- Deploying ChildChainStreamer contract to {connected.name} ---")
    streamer = ChildChainStreamer.deploy(
        DEPLOY_ACCT,
        gauge,
        Polygon.CCIP_DFX,
        {"from": DEPLOY_ACCT},
    )
    output_data["gauges"][label]["streamer"] = streamer.address
    write_contract(f"polygon{label[0].upper() + label[1:]}Streamer", streamer.address)
    return streamer


# deploy childchainreceiver
def deploy_receiver(
    streamer: ChildChainStreamer, label: str, verify_contracts=False
) -> ChildChainReceiver:
    print(f"--- Deploying Receiver contract to {connected.name} ---")
    receiver = ChildChainReceiver.deploy(
        Polygon.CCIP_ROUTER,
        streamer,
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT},
        publish_source=verify_contracts,
    )
    output_data["gauges"][label]["receiver"] = receiver.address
    write_contract(f"polygon{label[0].upper() + label[1:]}Receiver", receiver.address)
    return receiver


# grouped deployment of all contracts for an LP pair
def deploy_contract_set(
    gauge_logic: RewardsOnlyGauge, lpt_addr: str, label: str, verify: bool
):
    gauge = deploy_gauge(gauge_logic, lpt_addr, label, verify)
    streamer = deploy_streamer(gauge, label)
    receiver = deploy_receiver(streamer, label, verify)
    return receiver, streamer, gauge


def load_contract_set(receiver_addr: str, streamer_addr: str, gauge_addr: str):
    receiver = ChildChainReceiver.at(receiver_addr)
    streamer = ChildChainStreamer.at(streamer_addr)
    gauge = Contract.from_abi("RewardsOnlyGauge", gauge_addr, RewardsOnlyGauge.abi)
    return receiver, streamer, gauge


def configure(receiver, streamer, gauge):
    print(
        f"--- Configuring ChildChainStreamer contract with ChildChainReceiver as reward distributor ---"
    )
    # update authorized user for childchainstreamer rewards
    # DEV: This will be the address of the CCTP contract which is calling "notify_reward_amount"
    # on ChildChainStreamer
    streamer.set_reward_distributor(
        Polygon.CCIP_DFX, receiver.address, {"from": DEPLOY_ACCT}
    )

    print(f"--- Configuring RewardsOnlyGauge contract with DFX rewards ---")
    # set rewards contract on gauge
    # DEV: cannot be set while gauge has 0 deposits?
    gauge.set_rewards(
        streamer,
        streamer.signatures["get_reward"],
        [
            Polygon.CCIP_DFX,
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

    # Deploy all contracts
    # gauge_logic = deploy_gauge_implementation()
    # if connected.is_local:
    #     time.sleep(3)
    gauge_logic = load_gauge_implementation()

    verify_contracts = False if connected.is_local else True
    cadc_usdc_receiver, cadc_usdc_streamer, cadc_usdc_gauge = deploy_contract_set(
        gauge_logic, Polygon.CADC_USDC_LP, "cadcUsdc", verify_contracts
    )
    ngnc_usdc_receiver, ngnc_usdc_streamer, ngnc_usdc_gauge = deploy_contract_set(
        gauge_logic, Polygon.NGNC_USDC_LP, "ngncUsdc", verify_contracts
    )
    tryb_usdc_receiver, tryb_usdc_streamer, tryb_usdc_gauge = deploy_contract_set(
        gauge_logic, Polygon.TRYB_USDC_LP, "trybUsdc", verify_contracts
    )
    xsgd_usdc_receiver, xsgd_usdc_streamer, xsgd_usdc_gauge = deploy_contract_set(
        gauge_logic, Polygon.XSGD_USDC_LP, "xsgdUsdc", verify_contracts
    )

    # cadc_usdc_receiver, cadc_usdc_streamer, cadc_usdc_gauge = load_contract_set(
    #     Polygon.CADC_USDC_RECEIVER,
    #     Polygon.CADC_USDC_STREAMER,
    #     Polygon.CADC_USDC_GAUGE,
    # )
    # ngnc_usdc_receiver, ngnc_usdc_streamer, ngnc_usdc_gauge = load_contract_set(
    #     Polygon.NGNC_USDC_RECEIVER,
    #     Polygon.NGNC_USDC_STREAMER,
    #     Polygon.NGNC_USDC_GAUGE,
    # )
    # tryb_usdc_receiver, tryb_usdc_streamer, tryb_usdc_gauge = load_contract_set(
    #     Polygon.TRYB_USDC_RECEIVER,
    #     Polygon.TRYB_USDC_STREAMER,
    #     Polygon.TRYB_USDC_GAUGE,
    # )
    # xsgd_usdc_receiver, xsgd_usdc_streamer, xsgd_usdc_gauge = load_contract_set(
    #     Polygon.XSGD_USDC_RECEIVER,
    #     Polygon.XSGD_USDC_STREAMER,
    #     Polygon.XSGD_USDC_GAUGE,
    # )

    # Configure ChildChainStreamer distributor address (router), gauge
    # reward token address (ccDFX on L2), and whitelisting on ChildChainReceiver
    configure(cadc_usdc_receiver, cadc_usdc_streamer, cadc_usdc_gauge)
    configure(ngnc_usdc_receiver, ngnc_usdc_streamer, ngnc_usdc_gauge)
    configure(tryb_usdc_receiver, tryb_usdc_streamer, tryb_usdc_gauge)
    configure(xsgd_usdc_receiver, xsgd_usdc_streamer, xsgd_usdc_gauge)

    # Write output to file
    if not connected.is_local:
        with open(
            f"./scripts/polygon_l2_gauges_{int(time.time())}.json", "w"
        ) as output_f:
            json.dump(output_data, output_f, indent=4)
