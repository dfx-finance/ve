#!/usr/bin/env python
import json
import os
from typing import Union

from brownie import Contract, clDFX

from utils.constants_addresses import Ethereum


def assert_latest(key, value):
    fp = "./scripts/ve-addresses-latest.json"
    if not os.path.exists(fp):
        raise Exception(f"{fp} not found")
    data = json.load(open(fp))
    matches = data[key] == value
    if matches:
        # line in green
        print(f"\033[32;49m{key} - {value}\033[39;49m")
    else:
        # bold
        print(f"\033[1;39;49m{key}\033[0;39;49m")
        # second half of line in red
        print(f"  {data[key]} (log) != \033[31;49m{value} (cfg)\033[39;49m")


def log_configs_match():
    assert_latest("veDFX", Ethereum.VEDFX)
    assert_latest("veBoostProxy", Ethereum.VE_BOOST_PROXY)
    assert_latest("gaugeController", Ethereum.GAUGE_CONTROLLER)
    assert_latest("dfxDistributor", Ethereum.DFX_DISTRIBUTOR)

    assert_latest("cadcUsdcGauge", Ethereum.DFX_CADC_USDC_GAUGE)
    assert_latest("eurcUsdcGauge", Ethereum.DFX_EURC_USDC_GAUGE)
    assert_latest("gyenUsdcGauge", Ethereum.DFX_GYEN_USDC_GAUGE)
    assert_latest("nzdsUsdcGauge", Ethereum.DFX_NZDS_USDC_GAUGE)
    assert_latest("trybUsdcGauge", Ethereum.DFX_TRYB_USDC_GAUGE)
    assert_latest("xsgdUsdcGauge", Ethereum.DFX_XSGD_USDC_GAUGE)

    assert_latest("arbitrumCadcUsdcRootGauge", Ethereum.ARBITRUM_CADC_USDC_ROOT_GAUGE)
    assert_latest("arbitrumGyenUsdcRootGauge", Ethereum.ARBITRUM_GYEN_USDC_ROOT_GAUGE)

    assert_latest("polygonCadcUsdcRootGauge", Ethereum.POLYGON_CADC_USDC_ROOT_GAUGE)
    assert_latest("polygonNgncUsdcRootGauge", Ethereum.POLYGON_NGNC_USDC_ROOT_GAUGE)
    assert_latest("polygonTrybUsdcRootGauge", Ethereum.POLYGON_TRYB_USDC_ROOT_GAUGE)
    assert_latest("polygonXsgdUsdcRootGauge", Ethereum.POLYGON_XSGD_USDC_ROOT_GAUGE)


def main():
    log_configs_match()
