from brownie import DfxUpgradeableProxy

proxy = DfxUpgradeableProxy.at("0x599A1c5C41b0133fc97EC4911FcC17667128311B")
DfxUpgradeableProxy.publish_source(proxy)
