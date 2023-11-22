#!/usr/bin/env python
import brownie
from brownie import Contract, DfxUpgradeableProxy
from brownie import interface

from utils.config import INSTANCE_ID, DEPLOY_ACCT, DEPLOY_PROXY_ACCT
from utils.logger import load_inputs, load_outputs

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)

ETH_DEPLOYED_LABELS = [
    # "cadcUsdcGauge",
    # "eurcUsdcGauge",
    # "gbptUsdcGauge",
    # "gyenUsdcGauge",
    # "nzdsUsdcGauge",
    # "trybUsdcGauge",
    # "xidrUsdcGauge",
    # "xsgdUsdcGauge",
    # "arbitrumCadcUsdcRootGauge",
    # "arbitrumGyenUsdcRootGauge",
    # "arbitrumUsdceUsdcRootGauge",
    # "polygonCadcUsdcRootGauge",
    # "polygonNgncUsdcRootGauge",
    # "polygonTrybUsdcRootGauge",
    # "polygonXsgdUsdcRootGauge",
    # "polygonUsdceUsdcRootGauge",
]

POLYGON_DEPLOYED_LABELS = [
    # "cadcUsdcGauge",
    # "ngncUsdcGauge",
    # "trybUsdcGauge",
    # "xsgdUsdcGauge",
    # "usdceUsdcGauge",
]

ARBITRUM_DEPLOYED_LABELS = [
    # "cadcUsdcGauge",
    # "gyenUsdcGauge",
    # "usdceUsdcGauge",
]


def main():
    # DEPLOY_ACCT.transfer(DEPLOY_PROXY_ACCT, "1 ether")

    # for label in DEPLOYED_LABELS:
    proxy = Contract.from_abi(
        "DfxUpgradeableProxy",
        deployed.read_addr(ETH_DEPLOYED_LABELS[0]),
        interface.IDfxUpgradeableProxy.abi,
    )
    proxy.changeAdmin(existing.read_addr("multisig1"), {"from": DEPLOY_PROXY_ACCT})
    # print(proxy.admin(), {"from": DEPLOY_PROXY_ACCT})
