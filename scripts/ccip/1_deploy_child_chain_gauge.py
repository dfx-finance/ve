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
    accounts,
    ZERO_ADDRESS,
)

from utils.network import get_network_addresses, network_info

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

DEPLOY_ACCT = accounts.add(
    "0x0ac7fa86be251919f466d1313c31ecb341cbc09d55fcc2ffa18977619e9097fb"
)
PROXY_ADMIN_ACCT = accounts.add(
    "0xbdb5dd6948238006f64878060165682ed53067e602d15b07372ba276b8f06eef"
)
DFX_OFT = "0xc1c76a8c5bFDE1Be034bbcD930c668726E7C1987"  # clCCIP-LnM / Polygon Mumbai
CCIP_ROUTER = "0x70499c328e1E2a3c41108bd3730F6670a44595D1"  # Router / Polygon Mumbai
SEPOLIA_CHAIN_SELECTOR = 16015286601757825753


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
        DFX_OFT,
        {"from": DEPLOY_ACCT},
    )
    output_data["l2Gauge"]["streamer"] = streamer.address

    # deploy childchainreceiver
    receiver = ChildChainReceiver.deploy(
        CCIP_ROUTER, streamer, DEPLOY_ACCT, {"from": DEPLOY_ACCT}, publish_source=True
    )
    output_data["l2Gauge"]["receiver"] = receiver.address

    if not is_local_network:
        # Write output to file
        with open(
            f"./scripts/deployed_childchainstreamer_{int(time.time())}.json", "w"
        ) as output_f:
            json.dump(output_data, output_f, indent=4)

    return lpt, gauge_proxy, streamer, receiver


def configure(receiver, streamer, gauge):
    # update authorized user for childchainstreamer rewards
    # DEV: This will be the address of the CCTP contract which is calling "notify_reward_amount"
    # on ChildChainStreamer
    streamer.set_reward_distributor(DFX_OFT, receiver.address, {"from": DEPLOY_ACCT})

    # set rewards contract on gauge
    # DEV: cannot be set while gauge has 0 deposits?
    gauge.set_rewards(
        streamer,
        streamer.signatures["get_reward"],
        [
            DFX_OFT,
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


def load():
    lpt = ERC20LP.at("0xF15BBC3b5D2DF49b88967d2b574eF3d289a0138f")

    proxy = DfxUpgradeableProxy.at("0x8A8fe189B4722aE0c252565a6F72C7f3D7F7f903")
    gauge_proxy = Contract.from_abi("RewardsOnlyGauge", proxy, RewardsOnlyGauge.abi)
    streamer = ChildChainStreamer.at("0x8Fac0dE6e6F6E7714074f515E6dDb263B0fE12E0")
    receiver = ChildChainReceiver.at("0x078760e61Ab87ed32d1446d8fB955c74bF4379Ad")

    return lpt, gauge_proxy, streamer, receiver


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. CCIP Router address\n"
            "\t2. Reward token address\n"
        )
    )

    # lpt, gauge_proxy, streamer, receiver = deploy()
    # configure(receiver, streamer, gauge_proxy)

    lpt, gauge_proxy, streamer, receiver = load()
    receiver.whitelistSourceChain(SEPOLIA_CHAIN_SELECTOR, {"from": DEPLOY_ACCT})
    receiver.whitelistSender(CCIP_ROUTER, {"from": DEPLOY_ACCT})
