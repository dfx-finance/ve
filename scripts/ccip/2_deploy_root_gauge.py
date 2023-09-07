#!/usr/bin/env python
import json
import time

from brownie import RootGaugeCctp, accounts, interface, Contract, web3


from utils.network import get_network_addresses, network_info

addresses = get_network_addresses()
connected_network, is_local_network = network_info()

DEFAULT_GAUGE_TYPE = 0
DEFAULT_GAUGE_WEIGHT = 1e18
DEPLOY_ACCT = accounts.add(
    "0x0ac7fa86be251919f466d1313c31ecb341cbc09d55fcc2ffa18977619e9097fb"
)
PROXY_ADMIN_ACCT = accounts.add(
    "0xbdb5dd6948238006f64878060165682ed53067e602d15b07372ba276b8f06eef"
)
DFX_OFT = "0x466D489b6d36E7E3b824ef491C225F5830E81cC1"  # clCCIP-LnM / Ethereum Sepolia
CHILD_CHAIN_RECEIVER = "0x078760e61Ab87ed32d1446d8fB955c74bF4379Ad"
ROOT_GAUGE_TO_MIGRATE = "0x7C04E9A5650F5463AD9621DD44D8C4C362CF50B3"

output_data = {"gauges": {"rootGauge": {}}}


def deploy():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. root_gauge_cctp address\n"
            "\t2. DfxDistributor address\n"
        )
    )

    print(f"--- Deploying Root Gauge CCTP contract to {connected_network} ---")
    gauge = RootGaugeCctp.deploy(
        "L1 ETH/BTC Root Gauge",
        addresses.DFX_CCIP,
        DEPLOY_ACCT,
        addresses.CCIP_ROUTER,  # ccip router address
        12532609583862916517,  # target chain selector (polygon mumbai)
        CHILD_CHAIN_RECEIVER,  # child chain receiver address (l2 address)
        "0x0000000000000000000000000000000000000000",  # fee token address
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT},
        publish_source=True,
    )

    output_data["gauges"]["rootGauge"] = {
        "logic": gauge.address,
    }

    with open(
        f"./scripts/deployed_root_gauge_ccip_{int(time.time())}.json", "w"
    ) as output_f:
        json.dump(output_data, output_f, indent=4)


def migrate_assets(new_gauge):
    if ROOT_GAUGE_TO_MIGRATE:
        prev_gauge = Contract.from_abi(
            "RootGaugeCctp", ROOT_GAUGE_TO_MIGRATE, RootGaugeCctp.abi
        )
        dfx_bal = interface.IERC20(DFX_OFT).balanceOf(ROOT_GAUGE_TO_MIGRATE)
        prev_gauge.emergencyWithdraw(
            new_gauge.address, DFX_OFT, dfx_bal, {"from": DEPLOY_ACCT}
        )
        eth_bal = web3.eth.get_balance(prev_gauge.address)
        prev_gauge.emergencyWithdrawNative(
            new_gauge.address, eth_bal, {"from": DEPLOY_ACCT}
        )


def main():
    # gauge = deploy()
    gauge = RootGaugeCctp.at("0xccaF842839d0A879C3F17781d79be03CEe986395")
    migrate_assets(gauge)
