#!/usr/bin/env python
import json
import time

from brownie import ZERO_ADDRESS, DfxDistributor, DfxUpgradeableProxy, accounts
from brownie.network.gas.strategies import LinearScalingStrategy

from scripts import addresses, helper


LIFETIME_REWARDS_RATE = 1.5e5 * 1e18  # 150,000 DFX over 4 years
DISTRIBUTED_REWARDS = 0

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy("80 gwei", "250 gwei", 2.0)


output_data = {"distributor": {"logic": None, "proxy": None}}


def main():
    print((
        "Script 2 of 3:\n\n"
        "NOTE: This script expects configuration for:\n"
        "\t1. GaugeController address\n"
        "\t2. Total lifetime rewards of DFX token as `rate`\n"
        "\t3. Total amount of previously distributed rewards\n"
        "\t4. Governor and Guardian addresses"
    ))
    acct = accounts.load("anvil")
    fake_multisig = accounts[1]

    gauge_controller_address = helper.get_json_address(
        "deployed_gaugecontroller", ["gaugeController"])
    if not gauge_controller_address:
        return FileNotFoundError("No GaugeController deployments found")

    print("--- Deploying Distributor contract to Ethereum mainnet ---")
    dfx_distributor = DfxDistributor.deploy(
        {"from": acct, "gas_price": gas_strategy})
    output_data["distributor"]["logic"] = dfx_distributor.address

    distributor_initializer_calldata = dfx_distributor.initialize.encode_input(
        addresses.DFX,
        gauge_controller_address,
        LIFETIME_REWARDS_RATE,
        DISTRIBUTED_REWARDS,
        # needs another multisig to deal with access control behind proxy (ideally 2)
        addresses.DFX_MULTISIG,  # governor
        addresses.DFX_MULTISIG,  # guardian
        ZERO_ADDRESS   # delegate gauge for pulling type 2 gauge rewards
    )

    dfx_upgradable_proxy = DfxUpgradeableProxy.deploy(
        dfx_distributor.address,
        fake_multisig,
        distributor_initializer_calldata,
        {"from": acct, "gas_price": gas_strategy},
    )
    output_data["distributor"]["proxy"] = dfx_upgradable_proxy.address

    # Write output to file
    with open(f"./scripts/deployed_distributor_{int(time.time())}.json", "w") as output_f:
        json.dump(output_data, output_f, indent=4)
