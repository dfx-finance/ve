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
from .utils_ccip import DEPLOY_ACCT, PROXY_ADMIN_ACCT

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
    lpt = ERC20LP.at("0xF15BBC3b5D2DF49b88967d2b574eF3d289a0138f")
    output_data["l2Gauge"]["lpt"] = lpt.address

    # deploy l2 rewards-only gauge
    print(f"--- Deploying L2 gauge implementation contract to {connected_network} ---")
    gauge_implementation = RewardsOnlyGauge.deploy(
        {"from": DEPLOY_ACCT},
    )
    output_data["l2Gauge"]["gaugeImplementation"] = gauge_implementation.address

    # deploy gauge proxy and initialize
    print(f"--- Deploying L2 gauge proxy contract to {connected_network} ---")
    gauge_initializer_calldata = gauge_implementation.initialize.encode_input(
        DEPLOY_ACCT, lpt.address
    )
    proxy = DfxUpgradeableProxy.deploy(
        gauge_implementation.address,
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
        gauge_proxy.address,
        addresses.CCIP_DFX,
        {"from": DEPLOY_ACCT},
    )
    output_data["l2Gauge"]["streamer"] = streamer.address

    proxy = DfxUpgradeableProxy.at("0x8A8fe189B4722aE0c252565a6F72C7f3D7F7f903")
    gauge_proxy = Contract.from_abi("RewardsOnlyGauge", proxy, RewardsOnlyGauge.abi)
    streamer = ChildChainStreamer.at("0x8Fac0dE6e6F6E7714074f515E6dDb263B0fE12E0")

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
        addresses.DFX_CCIP, receiver.address, {"from": DEPLOY_ACCT}
    )

    # set rewards contract on gauge
    # DEV: cannot be set while gauge has 0 deposits?
    gauge.set_rewards(
        streamer,
        streamer.signatures["get_reward"],
        [
            addresses.DFX_CCIP,
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

    # # whitelist source chain and address on receiver
    # receiver.whitelistSourceChain(SEPOLIA_CHAIN_SELECTOR, {"from": DEPLOY_ACCT})
    # receiver.whitelistSender(CCIP_ROUTER, {"from": DEPLOY_ACCT})


## DEBUG
def load():
    lpt = ERC20LP.at("0xF15BBC3b5D2DF49b88967d2b574eF3d289a0138f")

    proxy = DfxUpgradeableProxy.at("0x8A8fe189B4722aE0c252565a6F72C7f3D7F7f903")
    gauge_proxy = Contract.from_abi("RewardsOnlyGauge", proxy, RewardsOnlyGauge.abi)
    streamer = ChildChainStreamer.at("0x8Fac0dE6e6F6E7714074f515E6dDb263B0fE12E0")
    receiver = ChildChainReceiver.at("0xa47562EBba9f246039d5f032d0DE56a97aA2e428")

    return lpt, gauge_proxy, streamer, receiver


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
    # lpt, gauge_proxy, streamer, receiver = load() # debug

    # # Configure ChildChainStreamer distributor address (router), gauge
    # # reward token address (ccDFX on L2), and whitelisting on ChildChainReceiver
    # configure(receiver, streamer, gauge_proxy)

    # lpt, gauge_proxy, streamer, receiver = load()
