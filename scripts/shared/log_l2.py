#!/usr/bin/env python
import json
import os
from typing import Union

from brownie import Contract, clDFX

from utils.constants_addresses import Arbitrum, Polygon


def assert_latest(key, value):
    fp = "./scripts/ve-addresses-latest.json"
    if not os.path.exists(fp):
        raise Exception(f"{fp} not found")
    data = json.load(open(fp))
    assert data[key] == value


def log_polygon_configs_match():
    assert_latest("polygonClDfx", Polygon.CCIP_DFX)
    assert_latest("polygonFakeLpt0", Polygon.DFX_CADC_USDC_LP)
    assert_latest("polygonFakeLpt1", Polygon.DFX_NGNC_USDC_LP)
    assert_latest("polygonFakeLpt2", Polygon.DFX_TRYB_USDC_LP)
    assert_latest("polygonFakeLpt3", Polygon.DFX_XSGD_USDC_LP)
    assert_latest("polygonFakeLpt3", Polygon.DFX_XSGD_USDC_LP)
    assert_latest("polygonFakeLpt3", Polygon.DFX_XSGD_USDC_LP)
    assert_latest("polygonFakeLpt3", Polygon.DFX_XSGD_USDC_LP)
    assert_latest("polygonFakeLpt3", Polygon.DFX_XSGD_USDC_LP)


def log_addresses_exist(addresses: Union[Arbitrum, Polygon]):
    _clDFX = Contract.from_abi("clDFX", addresses.CCIP_DFX, clDFX.abi)
    print(f"clDFX: {_clDFX.decimals()}")


def main():
    log_polygon_configs_match()
