#!/usr/bin/env python
from brownie import (
    Contract,
    GaugeController,
    LiquidityGaugeV4,
    CcipRootGauge,
    VeBoostProxy,
    VeDFX,
)

from utils.config import DEPLOY_ACCT, INSTANCE_ID
from utils.logger import load_inputs, load_outputs

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)

ETH_GAUGES = [
    deployed.read_addr("cadcUsdcGauge"),
    deployed.read_addr("eurcUsdcGauge"),
    deployed.read_addr("gbptUsdcGauge"),
    deployed.read_addr("gyenUsdcGauge"),
    deployed.read_addr("trybUsdcGauge"),
    deployed.read_addr("xidrUsdcGauge"),
    deployed.read_addr("xsgdUsdcGauge"),
]
ARBITRUM_GAUGES = [
    deployed.read_addr("arbitrumCadcUsdcRootGauge"),
    deployed.read_addr("arbitrumGyenUsdcRootGauge"),
]
POLYGON_GAUGES = [
    deployed.read_addr("polygonCadcUsdcRootGauge"),
    deployed.read_addr("polygonNgncUsdcRootGauge"),
    deployed.read_addr("polygonTrybUsdcRootGauge"),
    deployed.read_addr("polygonXsgdUsdcRootGauge"),
]
L2_GAUGES = [*ARBITRUM_GAUGES, *POLYGON_GAUGES]


def set_veDFX_admin():
    veDFX = Contract.from_abi("veDFX", existing.read_addr("veDFX"), VeDFX.abi)
    veDFX.commit_transfer_ownership(
        existing.read_addr("multisig0"), {"from": DEPLOY_ACCT}
    )
    veDFX.apply_transfer_ownership({"from": DEPLOY_ACCT})


def set_veBoostProxy_admin():
    veBoostProxy = Contract.from_abi(
        "veBoostProxy", deployed.read_addr("veBoostProxy"), VeBoostProxy.abi
    )
    veBoostProxy.commit_admin(existing.read_addr("multisig0"), {"from": DEPLOY_ACCT})
    veBoostProxy.accept_transfer_ownership({"from": existing.read_addr("multisig0")})


def set_gauge_controller_admin():
    gauge_controller = Contract.from_abi(
        "GaugeController", deployed.read_addr("gaugeController"), GaugeController.abi
    )
    gauge_controller.commit_transfer_ownership(
        existing.read_addr("multisig0"), {"from": DEPLOY_ACCT}
    )
    gauge_controller.accept_transfer_ownership(
        {"from": existing.read_addr("multisig0")}
    )


def set_eth_gauge_admin(gauge_addr: str):
    gauge = Contract.from_abi("LiquidityGaugeV4", gauge_addr, LiquidityGaugeV4.abi)
    gauge.commit_transfer_ownership(
        existing.read_addr("multisig0"), {"from": DEPLOY_ACCT}
    )
    gauge.accept_transfer_ownership({"from": existing.read_addr("multisig0")})


def set_l2_root_gauge_admin(gauge_addr: str):
    gauge = Contract.from_abi("RootGaugeCcip", gauge_addr, CcipRootGauge.abi)
    gauge.updateAdmin(existing.read_addr("multisig0"), {"from": DEPLOY_ACCT})


def add_l2_gauge_type():
    gauge_controller = Contract.from_abi(
        "GaugeController", deployed.read_addr("gaugeController"), GaugeController.abi
    )

    # add placeholder gauge type `1` to keep consistent with Angle distributor contract
    gauge_controller.add_type(
        "Staking Rewards",
        0,
        {"from": existing.read_addr("multisig0")},
    )
    # add new l2 gauge type to gauge controller
    gauge_controller.add_type(
        "L2 Liquidity Pools",
        1e18,
        {"from": existing.read_addr("multisig0")},
    )


def add_eth_gauge(gauge_addr: str):
    gauge_controller = Contract.from_abi(
        "GaugeController", deployed.read_addr("gaugeController"), GaugeController.abi
    )
    gauge_controller.add_gauge(
        gauge_addr,
        0,  # ETH gauge type
        1e18,  # Default weight
        {"from": existing.read_addr("multisig0")},
    )


def add_l2_root_gauge(gauge_addr: str):
    gauge_controller = Contract.from_abi(
        "GaugeController", deployed.read_addr("gaugeController"), GaugeController.abi
    )
    gauge_controller.add_gauge(
        gauge_addr,
        2,  # L2 gauge type
        1e18,  # Default weight
        {"from": existing.read_addr("multisig0")},
    )


def set_l2_root_gauge_distributor(gauge_addr: str):
    gauge = Contract.from_abi("RootGaugeCcip", gauge_addr, CcipRootGauge.abi)
    gauge.setDistributor(
        deployed.read_addr("dfxDistributor"), {"from": existing.read_addr("multisig0")}
    )


def main():
    # if network.is_local:
    #     fund_multisigs(DEPLOY_ACCT, [existing.read_addr("multisig0")])

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
