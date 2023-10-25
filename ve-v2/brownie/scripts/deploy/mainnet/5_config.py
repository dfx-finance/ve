#!/usr/bin/env python
from brownie import (
    Contract,
    GaugeController,
    LiquidityGaugeV4,
    RootGaugeCcip,
    VeBoostProxy,
    VeDFX,
)

from fork.utils.account import DEPLOY_ACCT
from utils.constants_addresses import Ethereum, EthereumLocalhost
from utils.helper import fund_multisigs
from utils.network import network_info

connected = network_info()
Ethereum = EthereumLocalhost if connected.is_local else Ethereum

ETH_GAUGES = [
    Ethereum.CADC_USDC_GAUGE,
    Ethereum.EURC_USDC_GAUGE,
    Ethereum.GBPT_USDC_GAUGE,
    Ethereum.GYEN_USDC_GAUGE,
    # Ethereum.NZDS_USDC_GAUGE,
    Ethereum.TRYB_USDC_GAUGE,
    Ethereum.XIDR_USDC_GAUGE,
    Ethereum.XSGD_USDC_GAUGE,
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


def set_veDFX_admin():
    veDFX = Contract.from_abi("veDFX", Ethereum.VEDFX, VeDFX.abi)
    veDFX.commit_transfer_ownership(Ethereum.DFX_MULTISIG_0, {"from": DEPLOY_ACCT})
    veDFX.apply_transfer_ownership({"from": DEPLOY_ACCT})


def set_veBoostProxy_admin():
    veBoostProxy = Contract.from_abi(
        "veBoostProxy", Ethereum.VEBOOST_PROXY, VeBoostProxy.abi
    )
    veBoostProxy.commit_admin(Ethereum.DFX_MULTISIG_0, {"from": DEPLOY_ACCT})
    veBoostProxy.accept_transfer_ownership({"from": Ethereum.DFX_MULTISIG_0})


def set_gauge_controller_admin():
    gauge_controller = Contract.from_abi(
        "GaugeController", Ethereum.GAUGE_CONTROLLER, GaugeController.abi
    )
    gauge_controller.commit_transfer_ownership(
        Ethereum.DFX_MULTISIG_0, {"from": DEPLOY_ACCT}
    )
    gauge_controller.accept_transfer_ownership({"from": Ethereum.DFX_MULTISIG_0})


def set_eth_gauge_admin(gauge_addr: str):
    gauge = Contract.from_abi("LiquidityGaugeV4", gauge_addr, LiquidityGaugeV4.abi)
    gauge.commit_transfer_ownership(Ethereum.DFX_MULTISIG_0, {"from": DEPLOY_ACCT})
    gauge.accept_transfer_ownership({"from": Ethereum.DFX_MULTISIG_0})


def set_l2_root_gauge_admin(gauge_addr: str):
    gauge = Contract.from_abi("RootGaugeCcip", gauge_addr, RootGaugeCcip.abi)
    gauge.updateAdmin(Ethereum.DFX_MULTISIG_0, {"from": DEPLOY_ACCT})


def add_l2_gauge_type():
    gauge_controller = Contract.from_abi(
        "GaugeController", Ethereum.GAUGE_CONTROLLER, GaugeController.abi
    )

    # add placeholder gauge type `1` to keep consistent with Angle distributor contract
    gauge_controller.add_type(
        "Staking Rewards",
        0,
        {"from": Ethereum.DFX_MULTISIG_0},
    )
    # add new l2 gauge type to gauge controller
    gauge_controller.add_type(
        "L2 Liquidity Pools",
        1e18,
        {"from": Ethereum.DFX_MULTISIG_0},
    )


def add_eth_gauge(gauge_addr: str):
    gauge_controller = Contract.from_abi(
        "GaugeController", Ethereum.GAUGE_CONTROLLER, GaugeController.abi
    )
    gauge_controller.add_gauge(
        gauge_addr,
        0,  # ETH gauge type
        1e18,  # Default weight
        {"from": Ethereum.DFX_MULTISIG_0},
    )


def add_l2_root_gauge(gauge_addr: str):
    gauge_controller = Contract.from_abi(
        "GaugeController", Ethereum.GAUGE_CONTROLLER, GaugeController.abi
    )
    gauge_controller.add_gauge(
        gauge_addr,
        2,  # L2 gauge type
        1e18,  # Default weight
        {"from": Ethereum.DFX_MULTISIG_0},
    )


def set_l2_root_gauge_distributor(gauge_addr: str):
    gauge = Contract.from_abi("RootGaugeCcip", gauge_addr, RootGaugeCcip.abi)
    gauge.setDistributor(Ethereum.DFX_DISTRIBUTOR, {"from": Ethereum.DFX_MULTISIG_0})


def main():
    # if network.is_local:
    #     fund_multisigs(DEPLOY_ACCT, [Ethereum.DFX_MULTISIG_0])

    # set_veDFX_admin()
    # set_veBoostProxy_admin()
    # set_gauge_controller_admin()

    # for gauge_addr in ETH_GAUGES:
    #     set_eth_gauge_admin(gauge_addr)
    # for gauge_addr in L2_GAUGES:
    #     set_l2_root_gauge_admin(gauge_addr)

    # #
    # # Add gauges to GaugeController
    # #
    # for gauge_addr in ETH_GAUGES:
    #     add_eth_gauge(gauge_addr)

    # add_l2_gauge_type()
    # for gauge_addr in L2_GAUGES:
    #     add_l2_root_gauge(gauge_addr)
    #     set_l2_root_gauge_distributor(gauge_addr)
    pass
