#!/usr/bin/env python
from brownie import ChildChainReceiver, clDFX, DfxUpgradeableProxy, RootGaugeCcip


def main():
    # receiver = ChildChainReceiver.at("0x2ac83d175bb12A11714319d6827b7C6D597e6504")
    # ChildChainReceiver.publish_source(receiver)

    # ChildChainStreamer (Vyper) -- cannot be verified

    # proxy = DfxUpgradeableProxy.at("0xB69f0Ae30b33e536EC435810241fd56FB49cEB8f")
    # DfxUpgradeableProxy.publish_source(proxy)

    # clDFX_ = clDFX.at("0x71EB1046607a2496A2fD48AB73D1973ee9FaDFf0")
    # clDFX.publish_source(clDFX_)

    rootGauge = RootGaugeCcip.at("0x5CFD640a991253bdB7ed181B0b48ae0a1c10753F")
    RootGaugeCcip.publish_source(rootGauge)
