#!/usr/bin/env python
import json
import os

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


def check_polygon_addresses_match():
    assert_latest("polygonClDfx", Polygon.CCIP_DFX)
    assert_latest("polygonFakeLpt0", Polygon.DFX_CADC_USDC_LP)
    assert_latest("polygonFakeLpt1", Polygon.DFX_NGNC_USDC_LP)
    assert_latest("polygonFakeLpt2", Polygon.DFX_TRYB_USDC_LP)
    assert_latest("polygonFakeLpt3", Polygon.DFX_XSGD_USDC_LP)


def check_arbitrum_addresses_match():
    assert_latest("arbitrumClDfx", Arbitrum.CCIP_DFX)
    assert_latest("arbitrumFakeLpt0", Arbitrum.DFX_CADC_USDC_LP)
    assert_latest("arbitrumFakeLpt1", Arbitrum.DFX_GYEN_USDC_LP)
