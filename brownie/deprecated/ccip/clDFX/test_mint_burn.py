#!/usr/bin/env python
from brownie import accounts, clDFX

from utils.gas import gas_strategy
from utils.network import get_network_addresses, network_info

addresses = get_network_addresses()
connected_network, is_local_network = network_info()

output_data = {"clDFX": None}


def main():
    DEPLOY_ACCT = accounts.load("cldfx")
    TEST_USER = "0x4210B1803f7CB057435fF1135F5dfdFBee086c27"

    clDFX_ = clDFX.at("0x6Ccc4Bb6F1862D7360F1536860B0Abd5030Acb22")
    clDFX_.setMinter(DEPLOY_ACCT, {"from": DEPLOY_ACCT, "gas_price": gas_strategy})

    # Deploy
    deployBalBefore = clDFX_.balanceOf(DEPLOY_ACCT)
    clDFX_.mint(DEPLOY_ACCT, 1e18, {"from": DEPLOY_ACCT, "gas_price": gas_strategy})
    deployBalDuring = clDFX_.balanceOf(DEPLOY_ACCT)
    clDFX_.burn(1e18, {"from": DEPLOY_ACCT, "gas_price": gas_strategy})
    deployBalAfter = clDFX_.balanceOf(DEPLOY_ACCT)

    # Test user
    testBalBefore = clDFX_.balanceOf(TEST_USER)
    clDFX_.mint(TEST_USER, 1e18, {"from": DEPLOY_ACCT, "gas_price": gas_strategy})
    testBalDuring = clDFX_.balanceOf(TEST_USER)
    clDFX_.burnFrom(TEST_USER, 1e18, {"from": DEPLOY_ACCT, "gas_price": gas_strategy})
    testBalAfter = clDFX_.balanceOf(TEST_USER)

    # # User mint
    # clDFX_.mint(TEST_USER, 1e18, {"from": TEST_USER, "gas_price": gas_strategy})

    # # User burn
    # clDFX_.mint(TEST_USER, 1e18, {"from": DEPLOY_ACCT, "gas_price": gas_strategy})
    # clDFX_.burn(1e18, {"from": TEST_USER, "gas_price": gas_strategy})

    print("Balance before (deploy user):", deployBalBefore)
    print("Balance during (deploy user):", deployBalDuring)
    print("Balance after (deploy user):", deployBalAfter)
    print("Balance before (test user):", testBalBefore)
    print("Balance during (test user):", testBalDuring)
    print("Balance after (test user):", testBalAfter)
