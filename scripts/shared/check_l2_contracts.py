#!/usr/bin/env python
import json
import os

from brownie import Contract, ChildChainStreamer, ChildChainReceiver, RewardsOnlyGauge
from typing import Union

from fork.utils.account import DEPLOY_ACCT
from utils.ccip import ETHEREUM_CHAIN_SELECTOR
from utils.constants_addresses import (
    Arbitrum,
    Polygon,
    ArbitrumLocalhost,
    PolygonLocalhost,
)
from utils.network import network_info

connected = network_info()
Arbitrum = ArbitrumLocalhost if connected.is_local else Arbitrum
Polygon = PolygonLocalhost if connected.is_local else Polygon


def assert_latest(key, value):
    fp = "./scripts/ve-addresses-latest.json"
    if not os.path.exists(fp):
        raise Exception(f"{fp} not found")
    data = json.load(open(fp))
    assert data[key] == value


def check_arbitrum_addresses_match():
    assert_latest("arbitrumClDfx", Arbitrum.CCIP_DFX)
    assert_latest("arbitrumFakeLpt0", Arbitrum.DFX_CADC_USDC_LP)
    assert_latest("arbitrumFakeLpt1", Arbitrum.DFX_GYEN_USDC_LP)
    assert_latest("arbitrumCadcUsdcReceiver", Arbitrum.CCIP_CADC_USDC_RECEIVER)
    assert_latest("arbitrumCadcUsdcStreamer", Arbitrum.CCIP_CADC_USDC_STREAMER)
    assert_latest("arbitrumCadcUsdcGauge", Arbitrum.DFX_CADC_USDC_GAUGE)
    assert_latest("arbitrumGyenUsdcReceiver", Arbitrum.CCIP_GYEN_USDC_RECEIVER)
    assert_latest("arbitrumGyenUsdcStreamer", Arbitrum.CCIP_GYEN_USDC_STREAMER)
    assert_latest("arbitrumGyenUsdcGauge", Arbitrum.DFX_GYEN_USDC_GAUGE)


def check_polygon_addresses_match():
    assert_latest("polygonClDfx", Polygon.CCIP_DFX)
    assert_latest("polygonFakeLpt0", Polygon.DFX_CADC_USDC_LP)
    assert_latest("polygonFakeLpt1", Polygon.DFX_NGNC_USDC_LP)
    assert_latest("polygonFakeLpt2", Polygon.DFX_TRYB_USDC_LP)
    assert_latest("polygonFakeLpt3", Polygon.DFX_XSGD_USDC_LP)
    assert_latest("polygonCadcUsdcReceiver", Polygon.CCIP_CADC_USDC_RECEIVER)
    assert_latest("polygonCadcUsdcStreamer", Polygon.CCIP_CADC_USDC_STREAMER)
    assert_latest("polygonCadcUsdcGauge", Polygon.DFX_CADC_USDC_GAUGE)
    assert_latest("polygonNgncUsdcReceiver", Polygon.CCIP_NGNC_USDC_RECEIVER)
    assert_latest("polygonNgncUsdcStreamer", Polygon.CCIP_NGNC_USDC_STREAMER)
    assert_latest("polygonNgncUsdcGauge", Polygon.DFX_NGNC_USDC_GAUGE)
    assert_latest("polygonTrybUsdcReceiver", Polygon.CCIP_TRYB_USDC_RECEIVER)
    assert_latest("polygonTrybUsdcStreamer", Polygon.CCIP_TRYB_USDC_STREAMER)
    assert_latest("polygonTrybUsdcGauge", Polygon.DFX_TRYB_USDC_GAUGE)
    assert_latest("polygonXsgdUsdcReceiver", Polygon.CCIP_XSGD_USDC_RECEIVER)
    assert_latest("polygonXsgdUsdcStreamer", Polygon.CCIP_XSGD_USDC_STREAMER)
    assert_latest("polygonXsgdUsdcGauge", Polygon.DFX_XSGD_USDC_GAUGE)


class Checks:
    def __init__(self, network: Union[Polygon, Arbitrum]):
        self.multisig = network.DFX_MULTISIG_0
        self.DFX = network.CCIP_DFX

    def check_receiver(self, receiver_addr, streamer_addr, root_gauge_addr):
        receiver = Contract.from_abi(
            "ChildChainReceiver", receiver_addr, ChildChainReceiver.abi
        )
        assert (
            receiver.streamer() == streamer_addr
        ), "ChildChainReceiver / Unexpected streamer address"
        assert receiver.owner() in [
            self.multisig,
            DEPLOY_ACCT,
        ], "ChildChainReceiver / Unexpected owner"

        assert (
            receiver.streamer() == streamer_addr
        ), "ChildChainReceiver / Unexpected streamer address"
        assert receiver.whitelistedSourceChains(
            ETHEREUM_CHAIN_SELECTOR
        ), "ChildChainReceiver / Source chain not whitelisted"
        assert receiver.whitelistedSenders(
            root_gauge_addr,
        ), "ChildChainReceiver / Sender not whitelisted"

    def check_streamer(self, streamer_addr, gauge_addr):
        streamer = Contract.from_abi(
            "ChildChainStreamer", streamer_addr, ChildChainStreamer.abi
        )
        assert streamer.owner() in [
            self.multisig,
            DEPLOY_ACCT,
        ], "ChildChainStreamer / Unexpected owner"
        assert (
            streamer.reward_receiver() == gauge_addr
        ), "ChildChainStreamer / Unexpected destination gauge"
        assert (
            streamer.reward_count() == 1
        ), "ChildChainStreamer / Unexpected number of reward tokens"
        assert (
            streamer.reward_tokens(0) == self.DFX,
        ), "ChildChainStreamer / Reward does not match DFX token"

    def check_gauge(self, gauge_addr, streamer_addr):
        gauge = Contract.from_abi("RewardsOnlyGauge", gauge_addr, RewardsOnlyGauge.abi)
        assert gauge.initialized(), "RewardsOnlyGauge / Not initialized"
        assert gauge.admin() in [
            self.multisig,
            DEPLOY_ACCT,
        ], "RewardsOnlyGauge / Unexpected admin"
        assert (
            gauge.reward_tokens(0) == self.DFX
        ), "RewardsOnlyGauge / Reward does not match DFX token"
        assert (
            gauge.reward_contract() == streamer_addr
        ), "RewardsOnlyGauge / Invalid DFX streamer"
