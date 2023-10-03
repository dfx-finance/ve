#!/usr/bin/env python
import json
import os

from brownie import (
    Contract,
    ZERO_ADDRESS,
    DfxDistributor,
    GaugeController,
    LiquidityGaugeV4,
    RootGaugeCcip,
    VeDFX,
    VeBoostProxy,
)
from brownie.exceptions import VirtualMachineError

from utils.ccip import ARBITRUM_CHAIN_SELECTOR, POLYGON_CHAIN_SELECTOR
from utils.constants_addresses import Ethereum, EthereumLocalhost
from utils.network import network_info

connected = network_info()

# override addresses when running on local fork
Ethereum = EthereumLocalhost if connected.is_local else Ethereum

PAIRS = [
    (Ethereum.DFX_CADC_USDC_LP, Ethereum.DFX_CADC_USDC_GAUGE),
    (Ethereum.DFX_EURC_USDC_LP, Ethereum.DFX_EURC_USDC_GAUGE),
    (Ethereum.DFX_GBPT_USDC_LP, Ethereum.DFX_GBPT_USDC_GAUGE),
    (Ethereum.DFX_GYEN_USDC_LP, Ethereum.DFX_GYEN_USDC_GAUGE),
    (Ethereum.DFX_NZDS_USDC_LP, Ethereum.DFX_NZDS_USDC_GAUGE),
    (Ethereum.DFX_TRYB_USDC_LP, Ethereum.DFX_TRYB_USDC_GAUGE),
    (Ethereum.DFX_XIDR_USDC_LP, Ethereum.DFX_XIDR_USDC_GAUGE),
    (Ethereum.DFX_XSGD_USDC_LP, Ethereum.DFX_XSGD_USDC_GAUGE),
]
ARBITRUM_GAUGES = [
    Ethereum.ARBITRUM_CADC_USDC_ROOT_GAUGE,
    Ethereum.ARBITRUM_GYEN_USDC_ROOT_GAUGE,
]
POLYGON_GAUGES = [
    Ethereum.POLYGON_CADC_USDC_ROOT_GAUGE,
    Ethereum.POLYGON_NGNC_USDC_ROOT_GAUGE,
    Ethereum.POLYGON_TRYB_USDC_ROOT_GAUGE,
    Ethereum.POLYGON_XSGD_USDC_ROOT_GAUGE,
]
L2_GAUGES = [*ARBITRUM_GAUGES, *POLYGON_GAUGES]


def _bold_str(text: str):
    return f"\033[1;39;49m{text}\033[0;39;49m"


def _green_str(text: str):
    return f"\033[32;49m{text}\033[39;49m"


def _red_str(text: str):
    return f"\033[31;49m{text}\033[39;49m"


def assert_latest(key, value):
    fp = "./scripts/ve-addresses-latest.json"
    if not os.path.exists(fp):
        raise Exception(f"{fp} not found")
    data = json.load(open(fp))
    matches = data[key] == value
    if matches:
        print(_green_str(f"{key} - {value}"))  # line in green
    else:
        print(_bold_str(key))  # bold
        print(
            # second half of line in red
            "  {expected} (json) != {val}".format(
                expected=data[key],
                val=_red_str(f"{value} (cfg)"),
            )
        )


def address_checks():
    assert_latest("veDFX", Ethereum.VEDFX)
    assert_latest("veBoostProxy", Ethereum.VEBOOST_PROXY)
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


def vedfx_checks():
    veDFX = Contract.from_abi("veDFX", Ethereum.VEDFX, VeDFX.abi)
    assert veDFX.token() == Ethereum.DFX, "veDFX / DFX addresses do not match"
    assert veDFX.admin() in [
        Ethereum.DFX_MULTISIG_0,
        "0x945D3D5CA590701C2C357309648Adcd70d4D8E9b",  # DEV: Kendrick deploy(!)
    ], "Unexpected admin"


# def veboost_checks():
#     veBoost = Contract.from_abi("veBoost", Ethereum.VEBOOST, VeBoost.abi)
#     assert veBoost.VE() == Ethereum.VEDFX, "veBoost / Unexpected veDFX"


def veboost_proxy_checks():
    veBoostProxy = Contract.from_abi(
        "veBoostProxy", Ethereum.VEBOOST_PROXY, VeBoostProxy.abi
    )
    assert (
        veBoostProxy.admin() == Ethereum.DFX_MULTISIG_0
    ), "veBoostProxy / Unexpected admin"
    assert (
        veBoostProxy.voting_escrow() == Ethereum.VEDFX
    ), "veBoostProxy / Unexpected veDFX"
    if Ethereum.VEBOOST:
        assert (
            veBoostProxy.delegation() == Ethereum.VEBOOST
        ), "veBoostProxy / Unexpected veBoost"


def gauge_controller_checks():
    gauge_controller = Contract.from_abi(
        "GaugeController", Ethereum.GAUGE_CONTROLLER, GaugeController.abi
    )
    assert (
        gauge_controller.admin() == Ethereum.DFX_MULTISIG_0
    ), "GaugeController / Unexpected admin"
    assert (
        gauge_controller.token() == Ethereum.DFX
    ), "GaugeController / DFX addresses do not match"
    # 29 gauges of Oct 3, 2023
    total_gauges = 14 if connected.is_local else 31
    assert (
        gauge_controller.n_gauges() == total_gauges
    ), "GaugeController / Unexpected number of gauges"

    # test ETH gauges are registered
    for _, gauge_addr in PAIRS:
        assert (
            gauge_controller.gauge_types(gauge_addr) == 0
        ), "GaugeController / ETH Gauge not registered"

    # test L2 root gauges are registered
    for gauge_addr in L2_GAUGES:
        try:
            gauge_controller.gauge_types(gauge_addr) == 0
        except VirtualMachineError:
            print("GaugeController / L2 Gauge not registered")


def dfx_distributor_checks():
    dfx_distributor = Contract.from_abi(
        "DfxDistributor", Ethereum.DFX_DISTRIBUTOR, DfxDistributor.abi
    )

    default_admin_role = dfx_distributor.DEFAULT_ADMIN_ROLE()
    governor_role = dfx_distributor.GOVERNOR_ROLE()
    guardian_role = dfx_distributor.GUARDIAN_ROLE()

    assert (
        dfx_distributor.getRoleAdmin(default_admin_role) == ZERO_ADDRESS
    ), "DfxDistributor / Default admin should have no admin"
    assert (
        dfx_distributor.getRoleAdmin(governor_role) == governor_role
    ), "DfxDistributor / Governor is not own admin"
    assert (
        dfx_distributor.getRoleAdmin(guardian_role) == governor_role
    ), "DfxDistributor / Governor is not Guardian admin"
    assert (
        dfx_distributor.hasRole(default_admin_role, Ethereum.DFX_MULTISIG_0) == False
    ), "DfxDistributor / Should not be default admin"
    assert dfx_distributor.hasRole(
        governor_role, Ethereum.DFX_MULTISIG_0
    ), "DfxDistributor / Multisig not governor"
    assert dfx_distributor.hasRole(
        guardian_role, Ethereum.DFX_MULTISIG_0
    ), "DfxDistributor / Multisig not guardian"
    assert (
        dfx_distributor.controller() == Ethereum.GAUGE_CONTROLLER
    ), "DfxDistributor / Unexpected gauge controller"
    assert (
        dfx_distributor.rewardToken() == Ethereum.DFX
    ), "DfxDistributor / DFX token is not reward token"


def eth_gauges_checks():
    for i, (lpt_addr, gauge_addr) in enumerate(PAIRS):
        gauge = Contract.from_abi("LiquidityGaugeV4", gauge_addr, LiquidityGaugeV4.abi)
        assert (
            gauge.admin() == Ethereum.DFX_MULTISIG_0
        ), "LiquidityGaugeV4 / Unexpected admin"
        assert (
            gauge.DFX() == Ethereum.DFX
        ), "LiquidityGaugeV4 / DFX token does not match"
        assert (
            gauge.voting_escrow() == Ethereum.VEDFX
        ), "LiquidityGaugeV4 / veDFX token does not match"
        assert (
            gauge.veBoost_proxy() == Ethereum.VEBOOST_PROXY
        ), "LiquidityGaugeV4 / veBoostProxy does not match"
        assert gauge.staking_token() == lpt_addr, "LiquidityGaugeV4 / Unexpected LPT"


def l2_root_gauges_check():
    for gauge_addr in L2_GAUGES:
        gauge = Contract.from_abi("RootGaugeCcip", gauge_addr, RootGaugeCcip.abi)
        assert (
            gauge.admin() == Ethereum.DFX_MULTISIG_0
        ), "RootGaugeCcip / Unexpected admin"
        assert gauge.DFX() == Ethereum.DFX, "RootGaugeCcip / DFX token does not match"
        # assert (
        #     gauge.router() == Ethereum.CCIP_ROUTER
        # ), "RootGaugeCcip / Unexpected CCIP router"
        assert (
            gauge.distributor() == Ethereum.DFX_DISTRIBUTOR
        ), "RootGaugeCcip / Unexpected distributor"

    for gauge_addr in ARBITRUM_GAUGES:
        gauge = Contract.from_abi("RootGaugeCcip", gauge_addr, RootGaugeCcip.abi)
        assert (
            gauge.destinationChain() == ARBITRUM_CHAIN_SELECTOR
        ), "RootGaugeCcip / Unexpected Arbitrum chain selector"

    for gauge_addr in POLYGON_GAUGES:
        gauge = Contract.from_abi("RootGaugeCcip", gauge_addr, RootGaugeCcip.abi)
        assert (
            gauge.destinationChain() == POLYGON_CHAIN_SELECTOR
        ), "RootGaugeCcip / Unexpected Polygon chain selector"


def main():
    address_checks()
    vedfx_checks()
    # veboost_checks()  # DEV: disabled until VeBoost contract added to branch
    veboost_proxy_checks()
    gauge_controller_checks()
    dfx_distributor_checks()
    eth_gauges_checks()
    l2_root_gauges_check()
