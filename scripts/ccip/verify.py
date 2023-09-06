#!/usr/bin/env python
from brownie import DfxUpgradeableProxy, RootGaugeCctp


def main():
    # proxy = DfxUpgradeableProxy.at("0x599A1c5C41b0133fc97EC4911FcC17667128311B")
    # DfxUpgradeableProxy.publish_source(proxy)

    gauge = RootGaugeCctp.at("0x5e0b8BC60CE0b6Cf5FdCD4bED7854B584B81651d")
    RootGaugeCctp.publish_source(gauge)
