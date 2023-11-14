#!/usr/bin/env python
from brownie import (
    Contract,
    DfxDistributor,
    DfxUpgradeableProxy,
    CcipRootGauge,
    MigrationReceiver,
)

from utils.config import DEPLOY_ACCT, DEPLOY_PROXY_ACCT, INSTANCE_ID
from utils.logger import load_outputs

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

    # proxy = DfxUpgradeableProxy.at(deployed.read_addr("arbitrumCadcUsdcRootGauge"))
    # DfxUpgradeableProxy.publish_source(proxy)

    # receiver = MigrationReceiver.at(deployed.read_addr("migrationReceiver"))
    # MigrationReceiver.publish_source(receiver)

    distributorLogic = DfxDistributor.at(deployed.read_addr("dfxDistributorLogic"))
    DfxDistributor.publish_source(distributorLogic)
