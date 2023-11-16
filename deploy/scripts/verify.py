#!/usr/bin/env python
from brownie import (
    Contract,
    ChildChainReceiver,
    ChildChainStreamer,
    DfxDistributor,
    DfxUpgradeableProxy,
    CcipRootGauge,
    MigrationReceiver,
)

from utils.config import DEPLOY_ACCT, DEPLOY_PROXY_ACCT, INSTANCE_ID
from utils.logger import load_inputs, load_outputs

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


def main():
    ##
    ## Replace below w/ contract to verify
    ##
    # rootGauge = CcipRootGauge.at(deployed.read_addr("rootGaugeLogic"))
    # CcipRootGauge.publish_source(rootGauge)

    # gauge = Contract.from_abi(
    #     "DfxUpgradeableProxy",
    #     deployed.read_addr("arbitrumCadcUsdcRootGauge"),
    #     DfxUpgradeableProxy.abi,
    # )
    # CcipRootGauge.publish_source(gauge)

    proxy = DfxUpgradeableProxy.at("0x1cf68E3794927c63D858d56CAe7Be9Eb97EB3006")
    DfxUpgradeableProxy.publish_source(proxy)

    # receiver = MigrationReceiver.at(deployed.read_addr("migrationReceiver"))
    # MigrationReceiver.publish_source(receiver)

    receiver = ChildChainReceiver.at("0xC0E65cD47C2C6053FA4F65C9Dd4371603C858C1a")
    ChildChainReceiver.publish_source(receiver)

    # distributorLogic = DfxDistributor.at(deployed.read_addr("dfxDistributorLogic"))
    # DfxDistributor.publish_source(distributorLogic)
