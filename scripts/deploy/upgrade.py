#!/usr/bin/env python
from brownie import DfxUpgradeableProxy, RootGaugeCctp, accounts

DEPLOY_ACCT = accounts.add(
    "0x0ac7fa86be251919f466d1313c31ecb341cbc09d55fcc2ffa18977619e9097fb"
)
DFX_PROXY_ADMIN = accounts.add(
    "0xbdb5dd6948238006f64878060165682ed53067e602d15b07372ba276b8f06eef"
)

gauge_implementation = RootGaugeCctp.deploy({"from": DEPLOY_ACCT}, publish_source=True)

proxy = DfxUpgradeableProxy.at("0xc213C26F330e67dCf4Df3727A343d3dc09a7700f")
proxy.upgradeTo(gauge_implementation.address, {"from": DFX_PROXY_ADMIN})
