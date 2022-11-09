#!/usr/bin/env python
from brownie import accounts

from scripts import contracts
from scripts.helper import (
    get_addresses,
    gas_strategy,
    load_dfx_token,
    DEPLOY_ACCT,
    load_usdc_token,
)
from utils.testing.token import mint_usdc


addresses = get_addresses()

DFX_MULTISIG = accounts.at(address=addresses.DFX_MULTISIG, force=True)
TOPUP_DFX_REWARDS = 4674.6575342466 * 1e18  # 1,706,250.00 / (365/7) epochs / 7 gauges
TRYB_USDC_REWARDS = 1000 * 1e6


def send_dfx(dfx, amount, from_account, to_account):
    dfx.transfer(to_account, amount, {"from": from_account, "gas_price": gas_strategy})
    print("Sender account DFX balance:", dfx.balanceOf(from_account) / 1e18)


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. DfxDistributor address\n"
        )
    )
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)
    dfx = load_dfx_token()
    usdc = load_usdc_token()

    # provide multisig with ether
    DEPLOY_ACCT.transfer(addresses.DFX_MULTISIG, "2 ether", gas_price=gas_strategy)

    # Distribute rewards to the distributor contract
    dfx.approve(
        dfx_distributor,
        1_000_000_000 * 1e18,
        {"from": DFX_MULTISIG, "gas_price": gas_strategy},
    )

    gauge = contracts.gauges()[4]

    usdc.approve(
        gauge,
        1_000_000_000 * 1e6,
        {"from": DFX_MULTISIG, "gas_price": gas_strategy},
    )
    mint_usdc(usdc, 1000 * 1e6, DFX_MULTISIG, DEPLOY_ACCT)

    dfx_distributor.passRewardToGauge(
        gauge,
        dfx,
        TOPUP_DFX_REWARDS,
        {"from": DFX_MULTISIG, "gas_price": gas_strategy},
    )
    gauge.add_reward(
        usdc, DFX_MULTISIG, {"from": DFX_MULTISIG, "gas_price": gas_strategy}
    )
    gauge.deposit_reward_token(
        usdc,
        TRYB_USDC_REWARDS,
        {"from": DFX_MULTISIG, "gas_price": gas_strategy},
    )
    print(gauge.reward_count())
    print(usdc.balanceOf(DFX_MULTISIG) / 1e6)
    print(usdc.balanceOf(gauge) / 1e6)


if __name__ == "_main__":
    main()
