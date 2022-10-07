#!/usr/bin/env python
import brownie
from brownie import network

from scripts.helper import get_json_address


GAUGE_IDS = None
if network.show_active() in ['ethereum', 'hardhat']:
    GAUGE_IDS = ['CADC_USDC', 'EURS_USDC', 'EUROC_USDC',
                 'NZDS_USDC', 'TRYB_USDC', 'XIDR_USDC', 'XSGD_USDC']
if network.show_active() == 'polygon-main':
    GAUGE_IDS = ['CADC_USDC', 'EURS_USDC',
                 'NZDS_USDC', 'TRYB_USDC', 'XSGD_USDC']


def veboost_proxy(address):
    return brownie.interface.IVeBoostProxy(address)


def gauge_controller(address):
    return brownie.interface.IGaugeController(address)


def dfx_distributor(address):
    return brownie.interface.IDfxDistributor(address)


def gauge(gauge_id):
    _address = get_json_address(
        'deployed_liquidity_gauges_v4', ['gauges', 'amm', gauge_id, 'proxy'])
    if not _address:
        return LookupError(f'No Gauge deployments for {gauge_id} found')
    return brownie.interface.ILiquidityGauge(_address)


def gauges():
    _gauges = [gauge(gauge_id) for gauge_id in GAUGE_IDS]
    return _gauges
