#!/usr/bin/env python
from brownie import (
    ERC20LP,
    RewardsOnlyGauge,
    DfxUpgradeableProxy,
    ChildChainStreamer,
    ChildChainReceiver,
    Contract,
    interface,
)

from utils.network import get_network_addresses, network_info
from ..utils_ccip import DEPLOY_ACCT, SEPOLIA_CHAIN_SELECTOR

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
            acct.balance >= min_bal
        ), f"Insufficient balance: {acct.balance} (must be >= {min_bal}))"
    else:
        assert (
            acct.balance > min_bal
        ), f"Insufficient balance: {acct.balance} (must be > ({min_bal}))"


def load():
    lpt = ERC20LP.at(addresses.DFX_ETH_BTC_LP)
    proxy = DfxUpgradeableProxy.at(addresses.DFX_ETH_BTC_GAUGE)
    gauge_proxy = Contract.from_abi("RewardsOnlyGauge", proxy, RewardsOnlyGauge.abi)
    streamer = ChildChainStreamer.at(addresses.CCIP_STREAMER)
    receiver = ChildChainReceiver.at(addresses.CCIP_RECEIVER)
    return lpt, gauge_proxy, streamer, receiver


def check_setup(lpt, gauge_proxy, streamer, receiver):
    assert_eq(lpt.address, addresses.DFX_ETH_BTC_LP, "LPT does not match")
    assert_eq(
        gauge_proxy.lp_token(),
        addresses.DFX_ETH_BTC_LP,
        "Gauge LPT does not match",
    )
    assert_eq(
        gauge_proxy.reward_tokens(0), addresses.CCIP_DFX, "Reward token does not match"
    )
    assert_eq(streamer.reward_count(), 1, "Unexpected number of gauge reward tokens")
    assert_eq(
        streamer.reward_tokens(0),
        addresses.CCIP_DFX,
        "Gauge reward token does not match",
    )
    assert_eq(
        streamer.reward_data(addresses.CCIP_DFX)[0],
        addresses.CCIP_RECEIVER,
        "Gauge reward token distributor does not match",
    )
    assert_eq(
        streamer.reward_receiver(),
        addresses.DFX_ETH_BTC_GAUGE,
        "Streamer receiver gauge does not match",
    )
    assert_eq(receiver.owner(), DEPLOY_ACCT, "Unexpected owner")
    assert_eq(receiver.streamer(), streamer.address, "Streamer does not match")
    assert_eq(receiver.owner(), DEPLOY_ACCT, "Unexpected owner")
    assert_eq(
        receiver.whitelistedSourceChains(SEPOLIA_CHAIN_SELECTOR),
        True,
        "Chain not whitelisted",
    )
    assert_eq(
        receiver.whitelistedSenders(addresses.CCIP_ROUTER),
        True,
        "Sender not whitelisted",
    )
    assert_bal(receiver, addresses.CCIP_DFX, 0)
    assert_bal_eth(receiver, 0)
    print("All tests passed.")


def main():
    lpt, gauge_proxy, streamer, receiver = load()  # debug
    check_setup(lpt, gauge_proxy, streamer, receiver)
