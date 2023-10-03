#!/usr/bin/env python
from ..shared.check_l2_contracts import check_polygon_addresses_match, Checks

from utils.constants_addresses import (
    Ethereum,
    Polygon,
    EthereumLocalhost,
    PolygonLocalhost,
)
from utils.network import network_info

connected = network_info()
Ethereum = EthereumLocalhost if connected.is_local else Ethereum
Polygon = PolygonLocalhost if connected.is_local else Polygon

GAUGE_SETS = [
    (
        Ethereum.POLYGON_CADC_USDC_ROOT_GAUGE,
        Polygon.CCIP_CADC_USDC_RECEIVER,
        Polygon.CCIP_CADC_USDC_STREAMER,
        Polygon.DFX_CADC_USDC_GAUGE,
    ),
    (
        Ethereum.POLYGON_NGNC_USDC_ROOT_GAUGE,
        Polygon.CCIP_NGNC_USDC_RECEIVER,
        Polygon.CCIP_NGNC_USDC_STREAMER,
        Polygon.DFX_NGNC_USDC_GAUGE,
    ),
    (
        Ethereum.POLYGON_TRYB_USDC_ROOT_GAUGE,
        Polygon.CCIP_TRYB_USDC_RECEIVER,
        Polygon.CCIP_TRYB_USDC_STREAMER,
        Polygon.DFX_TRYB_USDC_GAUGE,
    ),
    (
        Ethereum.POLYGON_XSGD_USDC_ROOT_GAUGE,
        Polygon.CCIP_XSGD_USDC_RECEIVER,
        Polygon.CCIP_XSGD_USDC_STREAMER,
        Polygon.DFX_XSGD_USDC_GAUGE,
    ),
]


def main():
    check_polygon_addresses_match()

    checks = Checks(Polygon)
    for root_gauge_addr, receiver_addr, streamer_addr, gauge_addr in GAUGE_SETS:
        checks.check_receiver(receiver_addr, streamer_addr, root_gauge_addr)
        checks.check_streamer(streamer_addr, gauge_addr)
        checks.check_gauge(gauge_addr, streamer_addr)
