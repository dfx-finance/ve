#!/usr/bin/env python
import json
import time

from brownie import (
    ERC20LP,
    RewardsOnlyGauge,
    DfxUpgradeableProxy,
    ChildChainStreamer,
    ChildChainReceiver,
    Contract,
    ZERO_ADDRESS,
)

from utils.network import get_network_addresses, network_info
from .utils_ccip import DEPLOY_ACCT, PROXY_ADMIN_ACCT, SEPOLIA_CHAIN_SELECTOR

addresses = get_network_addresses()
connected_network, is_local_network = network_info()

output_data = {
    "l2Gauge": {
        "lpt": None,
        "receiver": None,
        "streamer": None,
        "gaugeImplementation": None,
        "gaugeProxy": None,
    }
}


def deploy():
    # deploy fake LPT
    print(f"--- Deploying fake LPT contract to {connected_network} ---")
    # name = "DFX Fake LPT"
    # symbol = "dfx-l2-lpt-fake"
    # lpt = ERC20LP.deploy(name, symbol, 18, 1e9, {"from": DEPLOY_ACCT})
    lpt = ERC20LP.at(addresses.DFX_ETH_BTC_LP)
    output_data["l2Gauge"]["lpt"] = lpt.address

    # deploy l2 rewards-only gauge
    print(f"--- Deploying L2 gauge implementation contract to {connected_network} ---")
    gauge = RewardsOnlyGauge.deploy(
        {"from": DEPLOY_ACCT},
    )
    output_data["l2Gauge"]["gaugeImplementation"] = gauge.address

    # deploy gauge proxy and initialize
    print(f"--- Deploying L2 gauge proxy contract to {connected_network} ---")
    gauge_initializer_calldata = gauge.initialize.encode_input(DEPLOY_ACCT, lpt)
    proxy = DfxUpgradeableProxy.deploy(
        gauge.address,
        PROXY_ADMIN_ACCT,
        gauge_initializer_calldata,
        {"from": DEPLOY_ACCT},
        publish_source=True,
    )
    gauge_proxy = Contract.from_abi("RewardsOnlyGauge", proxy, RewardsOnlyGauge.abi)
    output_data["l2Gauge"]["gaugeProxy"] = gauge_proxy.address

    # deploy childchainstreamer
    streamer = ChildChainStreamer.deploy(
        DEPLOY_ACCT,
        gauge_proxy,
        addresses.CCIP_DFX,
        {"from": DEPLOY_ACCT},
    )
    output_data["l2Gauge"]["streamer"] = streamer.address

    # deploy childchainreceiver
    receiver = ChildChainReceiver.deploy(
        addresses.CCIP_ROUTER,
        streamer,
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT},
        publish_source=True,
    )
    output_data["l2Gauge"]["receiver"] = receiver.address

    # Write output to file
    if not is_local_network:
        with open(
            f"./scripts/deployed_childchainstreamer_{int(time.time())}.json", "w"
        ) as output_f:
            json.dump(output_data, output_f, indent=4)

    return lpt, gauge_proxy, streamer, receiver


def configure(receiver, streamer, gauge):
    # update authorized user for childchainstreamer rewards
    # DEV: This will be the address of the CCTP contract which is calling "notify_reward_amount"
    # on ChildChainStreamer
    streamer.set_reward_distributor(
        addresses.CCIP_DFX, receiver.address, {"from": DEPLOY_ACCT}
    )

    # set rewards contract on gauge
    # DEV: cannot be set while gauge has 0 deposits?
    gauge.set_rewards(
        streamer,
        streamer.signatures["get_reward"],
        [
            addresses.CCIP_DFX,
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

    # whitelist source chain and address on receiver
    receiver.whitelistSourceChain(SEPOLIA_CHAIN_SELECTOR, {"from": DEPLOY_ACCT})
    receiver.whitelistSender(addresses.CCIP_ROUTER, {"from": DEPLOY_ACCT})


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. CCIP Router address\n"
            "\t2. Reward token address\n"
        )
    )

    # Deploy all contracts
    lpt, gauge_proxy, streamer, receiver = deploy()

    # Configure ChildChainStreamer distributor address (router), gauge
    # reward token address (ccDFX on L2), and whitelisting on ChildChainReceiver
    configure(receiver, streamer, gauge_proxy)

    print(f"LPT: {lpt.address}")
    print(f"LPT: {gauge_proxy.address}")
    print(f"LPT: {streamer.address}")
    print(f"LPT: {receiver.address}")
