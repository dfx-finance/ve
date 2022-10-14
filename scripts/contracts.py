#!/usr/bin/env python
import brownie
from brownie import network

from scripts import addresses


GAUGE_ADDRESSES = None
if network.show_active() in ['ethereum', 'mainnet', 'hardhat']:
    GAUGE_ADDRESSES = [
        addresses.Ethereum.DFX_CADC_USDC_GAUGE,
        addresses.Ethereum.DFX_EUROC_USDC_GAUGE,
        addresses.Ethereum.DFX_GYEN_USDC_GAUGE,
        addresses.Ethereum.DFX_NZDS_USDC_GAUGE,
        addresses.Ethereum.DFX_TRYB_USDC_GAUGE,
        addresses.Ethereum.DFX_XIDR_USDC_GAUGE,
        addresses.Ethereum.DFX_XSGD_USDC_GAUGE,
    ]
elif network.show_active() == 'polygon-main':
    GAUGE_ADDRESSES = [
        addresses.Polygon.DFX_CADC_USDC_GAUGE,
        addresses.Polygon.DFX_EURS_USDC_GAUGE,
        addresses.Polygon.DFX_NZDS_USDC_GAUGE,
        addresses.Polygon.DFX_TRYB_USDC_GAUGE,
        addresses.Polygon.DFX_XSGD_USDC_GAUGE,
    ]
# elif network.show_active() == 'hardhat':
#     GAUGE_ADDRESSES = [
#         addresses.Localhost.DFX_CADC_USDC_GAUGE,
#         addresses.Localhost.DFX_EUROC_USDC_GAUGE,
#         addresses.Localhost.DFX_GYEN_USDC_GAUGE,
#         addresses.Localhost.DFX_NZDS_USDC_GAUGE,
#         addresses.Localhost.DFX_TRYB_USDC_GAUGE,
#         addresses.Localhost.DFX_XIDR_USDC_GAUGE,
#         addresses.Localhost.DFX_XSGD_USDC_GAUGE,
#     ]


def veboost_proxy(address):
    return brownie.interface.IVeBoostProxy(address)


def gauge_controller(address):
    return brownie.interface.IGaugeController(address)


def dfx_distributor(address):
    return brownie.interface.IDfxDistributor(address)


def gauge(address):
    return brownie.interface.ILiquidityGauge(address)


def gauges():
    return [gauge(gauge_addr) for gauge_addr in GAUGE_ADDRESSES]

