#!/usr/bin/env python
from brownie import accounts

# Test deploy accounts
# WARNING: contains disposable private keys
DEPLOY_ACCT = accounts.add(
    "0x0ac7fa86be251919f466d1313c31ecb341cbc09d55fcc2ffa18977619e9097fb"
)
PROXY_ADMIN_ACCT = accounts.add(
    "0xbdb5dd6948238006f64878060165682ed53067e602d15b07372ba276b8f06eef"
)

# Chain selectors
SEPOLIA_CHAIN_SELECTOR = 16015286601757825753
MUMBAI_CHAIN_SELECTOR = 12532609583862916517
