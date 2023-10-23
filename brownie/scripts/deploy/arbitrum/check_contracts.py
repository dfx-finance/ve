#!/usr/bin/env python
from ..shared.check_l2_contracts import check_arbitrum_addresses_match, Checks

from utils.constants_addresses import (
    Ethereum,
    Arbitrum,
    EthereumLocalhost,
    ArbitrumLocalhost,
)
from utils.network import network_info

connected = network_info()
Ethereum = EthereumLocalhost if network.is_local else Ethereum
Arbitrum = ArbitrumLocalhost if network.is_local else Arbitrum

GAUGE_SETS = [
    (
        Ethereum.ARBITRUM_CADC_USDC_ROOT_GAUGE,
        Arbitrum.CCIP_CADC_USDC_RECEIVER,
        Arbitrum.CCIP_CADC_USDC_STREAMER,
        Arbitrum.DFX_CADC_USDC_GAUGE,
    ),
    (
        Ethereum.ARBITRUM_GYEN_USDC_ROOT_GAUGE,
        Arbitrum.CCIP_GYEN_USDC_RECEIVER,
        Arbitrum.CCIP_GYEN_USDC_STREAMER,
        Arbitrum.DFX_GYEN_USDC_GAUGE,
    ),
]


def main():
    check_arbitrum_addresses_match()

    checks = Checks(Arbitrum)
    for root_gauge_addr, receiver_addr, streamer_addr, gauge_addr in GAUGE_SETS:
        checks.check_receiver(receiver_addr, streamer_addr, root_gauge_addr)
        checks.check_streamer(streamer_addr, gauge_addr)
        checks.check_gauge(gauge_addr, streamer_addr)
