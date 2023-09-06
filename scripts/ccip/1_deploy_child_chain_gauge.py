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
)

from utils import contracts
from utils.gas import gas_strategy, verify_gas_strategy
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


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. CCIP Router address\n"
            "\t2. Reward token address\n"
        )
    )
    if not is_local_network:
        verify_gas_strategy()
    should_verify = not is_local_network

    # deploy fake LPT
    print(f"--- Deploying fake LPT contract to {connected_network} ---")
    name = "DFX Fake LPT"
    symbol = "dfx-l2-lpt-fake"
    lpt = ERC20LP.deploy(name, symbol, 18, 1e9, {"from": DEPLOY_ACCT})
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
        DEPLOY_ACCT, lpt
    )
    proxy = DfxUpgradeableProxy.deploy(
        gauge_implementation.address,
        PROXY_ADMIN_ACCT,
        gauge_initializer_calldata,
        {"from": DEPLOY_ACCT},
    )
    gauge_proxy = Contract.from_abi("RewardsOnlyGauge", proxy, RewardsOnlyGauge.abi)
    output_data["l2Gauge"]["gaugeProxy"] = gauge_proxy.address

    # deploy childchainstreamer
    streamer = ChildChainStreamer.deploy(
        DEPLOY_ACCT,
        gauge_proxy.address,
        DFX_OFT,
        CCIP_ROUTER,
        {"from": DEPLOY_ACCT},
    )
    output_data["l2Gauge"]["streamer"] = streamer.address

    # deploy childchainreceiver
    receiver = ChildChainReceiver.deploy(
        CCIP_ROUTER, streamer, DEPLOY_ACCT, {"from": DEPLOY_ACCT}
    )
    output_data["l2Gauge"]["receiver"] = receiver.address

    if not is_local_network:
        # Write output to file
        with open(
            f"./scripts/deployed_childchainstreamer_{int(time.time())}.json", "w"
        ) as output_f:
            json.dump(output_data, output_f, indent=4)
