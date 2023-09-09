#!/usr/bin/env python
from brownie import (
    DfxUpgradeableProxy,
    RootGaugeCcip,
    interface,
    Contract,
    ZERO_ADDRESS,
)

from utils.constants_addresses import Mumbai
from utils.network import get_network_addresses, network_info
from ..utils_ccip import DEPLOY_ACCT, MUMBAI_CHAIN_SELECTOR

addresses = get_network_addresses()
connected_network, is_local_network = network_info()


def assert_eq(a, b, err):
    assert a == b, f"{err}: {a} != {b}"


def assert_bal(addr, token, min_bal, inclusive=False):
    bal = interface.IERC20(token).balanceOf(addr)
    if inclusive:
        assert bal >= min_bal, f"Insufficient balance: {bal} (must be >= {min_bal})"
    else:
        assert bal > min_bal, f"Insufficient balance: {bal} (must be > {min_bal})"


def assert_bal_eth(acct, min_bal, inclusive=False):
    if inclusive:
        assert (
            acct.balance() >= min_bal
        ), f"Insufficient balance: {acct.balance} (must be >= {min_bal}))"
    else:
        assert (
            acct.balance() > min_bal
        ), f"Insufficient balance: {acct.balance} (must be > ({min_bal}))"


def load():
    proxy = DfxUpgradeableProxy.at(addresses.MUMBAI_ETH_BTC_ROOT_GAUGE)
    root_gauge = Contract.from_abi("RootGaugeCcip", proxy, RootGaugeCcip.abi)
    return root_gauge


def check_setup(root_gauge, debugging=False):
    assert_eq(
        root_gauge.address,
        addresses.MUMBAI_ETH_BTC_ROOT_GAUGE,
        "Root gauge does not match",
    )
    # # Deployed version
    # assert_eq(
    #     root_gauge_proxy.distributor(),
    #     addresses.DFX_DISTRIBUTOR,
    #     "Distributor does not match",
    # )
    assert_eq(
        root_gauge.distributor(),
        DEPLOY_ACCT,
        "Distributor does not match",
    )  # DEBUG distrbutor set to deploy account
    assert_eq(
        root_gauge.destinationChain(),
        MUMBAI_CHAIN_SELECTOR,
        "Destination chain selector does not match",
    )
    assert_eq(
        root_gauge.destination(),
        Mumbai.CCIP_RECEIVER,
        "Destination receiver does not match",
    )
    assert_eq(root_gauge.DFX(), addresses.CCIP_DFX, "Reward token does not match")
    assert_eq(root_gauge.feeToken(), ZERO_ADDRESS, "Fee token does not match")
    assert_eq(root_gauge.admin(), DEPLOY_ACCT, "Unexpected admin address")

    if debugging:
        assert_bal(root_gauge, addresses.CCIP_DFX, 0)
        assert_bal_eth(root_gauge, 0)

    print("All tests passed.")


def main():
    root_gauge = load()
    check_setup(root_gauge, debugging=False)
