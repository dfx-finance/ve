#!/usr/bin/env python
from datetime import datetime, timezone

from brownie import accounts, DfxUpgradeableProxy

from scripts import contracts
from scripts.helper import (
    get_addresses,
    gas_strategy,
    log_distributor_info,
    log_gauges_info,
)
from utils.chain import fastforward_chain

addresses = get_addresses()
HARDHAT_ACCT = accounts.load("hardhat")
MULTISIG_ACCT = accounts.at(addresses.DFX_MULTISIG, force=True)
PROXY_MULTISIG_ACCT = accounts[7]  # a random account


###
### Contract helpers
###
def enable_distributions():
    print("--- Enabling Gauge Distributions -------------------------")
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    if not dfx_distributor.distributionsOn():
        dfx_distributor.toggleDistributions(
            {"from": MULTISIG_ACCT, "gas_price": gas_strategy}
        )
        print(f"DFX distributions are enabled: {dfx_distributor.distributionsOn()}")
    else:
        print("DFX distribtions already enabled, skipping...")
    print("")


def disable_gauges(gauge_addresses):
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    print("--- Disabling Gauges -------------------------")
    for label, gauge_addr in gauge_addresses:
        if not dfx_distributor.killedGauges(gauge_addr):
            dfx_distributor.toggleGauge(
                gauge_addr, {"from": MULTISIG_ACCT, "gas_price": gas_strategy}
            )
            print(
                f"{label} gauge is killed: {dfx_distributor.killedGauges(gauge_addr)}"
            )
        else:
            print(f"{label} gauge already killed, skipped")
    print("")


def enable_gauges(gauge_addresses):
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    print("--- Enabling Gauges -------------------------")
    for label, gauge_addr in gauge_addresses:
        if dfx_distributor.killedGauges(gauge_addr):
            dfx_distributor.toggleGauge(
                gauge_addr, {"from": MULTISIG_ACCT, "gas_price": gas_strategy}
            )
            print(
                f"{label} gauge is enabled: {not dfx_distributor.killedGauges(gauge_addr)}"
            )
        else:
            print(f"{label} gauge already enabled, skipped")
    print("")


def zero_existing_gauge_weights(gauge_addresses):
    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)

    print("--- Zero Gauges Weights -------------------------")
    for label, gauge_addr in gauge_addresses:
        gauge_controller.change_gauge_weight(
            gauge_addr,
            0,
            {"from": MULTISIG_ACCT, "gas_price": gas_strategy, "silent": True},
        )
        print(f"{label} gauge weight: {gauge_controller.get_gauge_weight(gauge_addr)}")
    print("")


def set_gauges_weights(gauge_addresses, weights):
    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)

    print("--- Set Gauges Weights -------------------------")
    for i, (label, gauge_addr) in enumerate(gauge_addresses):
        gauge_controller.change_gauge_weight(
            gauge_addr,
            weights[i],
            {"from": MULTISIG_ACCT, "gas_price": gas_strategy, "silent": True},
        )
        print(f"{label} gauge weight: {gauge_controller.get_gauge_weight(gauge_addr)}")
    print("")


def distribute_rewards(gauge_addresses):
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)
    active_gauge_addresses = []
    for _, addr in gauge_addresses:
        if dfx_distributor.killedGauges(addr) == False:
            active_gauge_addresses.append(addr)

    print("--- Distribute Gauge Rewards -------------------------")
    dfx_distributor.distributeRewardToMultipleGauges(
        active_gauge_addresses, {"from": MULTISIG_ACCT, "gas_price": gas_strategy}
    )
    print("")


def update_epoch():
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)
    dfx_distributor.updateMiningParameters(
        {"from": MULTISIG_ACCT, "gas_price": gas_strategy}
    )


def checkpoint_rewards():
    gauges = contracts.gauges()
    for g in gauges:
        g.user_checkpoint(
            addresses.DFX_MULTISIG,
            {"from": MULTISIG_ACCT, "gas_price": gas_strategy},
        )


def deploy_proxied_gauges(lp_addresses):
    # deploy gauge logic
    gauge_logic = contracts.gauge("0x71c0ddBF6da72a67C29529d6f67f97C00c4751D5")

    # deploy gauge behind proxy
    proxied_gauges = []
    for label, lp_addr in lp_addresses:
        print(f"--- Deploying LiquidityGaugeV4 proxy contract for {label} ---")
        gauge_initializer_calldata = gauge_logic.initialize.encode_input(
            lp_addr,
            MULTISIG_ACCT,
            addresses.DFX,
            addresses.VOTE_ESCROW,
            addresses.VE_BOOST_PROXY,
            addresses.DFX_DISTRIBUTOR,
        )
        dfx_upgradeable_proxy = DfxUpgradeableProxy.deploy(
            gauge_logic.address,
            PROXY_MULTISIG_ACCT,
            gauge_initializer_calldata,
            {"from": MULTISIG_ACCT, "gas_price": gas_strategy},
            publish_source=False,
        )
        proxied_gauges.append((label, dfx_upgradeable_proxy))
    return proxied_gauges


def add_to_gauge_controller(new_gauges):
    default_gauge_type = 0
    default_gauge_weight = 1e18
    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)
    for label, g in new_gauges:
        print(f"--- Adding {label} LiquidityGaugeV4 to GaugeController ---")
        gauge_controller.add_gauge(
            g.address,
            default_gauge_type,
            default_gauge_weight,
            {"from": MULTISIG_ACCT, "gas_price": gas_strategy},
        )


##
## Tests
##
# Q: At initial post-hack state, was the current epoch updated correctly?
# A: Yes
def test_initial_state_epoch():
    update_epoch()
    log_distributor_info()

    # Fastforward chain and ensure existing gauges receive no distributions
    end_dt = datetime(2022, 11, 11, 1, 35, 40, tzinfo=timezone.utc)
    fastforward_chain(end_dt)

    # Distribute rewards on November 17 at 00:35 UTC
    update_epoch()
    log_distributor_info()


##
## Main
##
def main():
    existing_gauges = [
        ("CADC_USDC", addresses.DFX_CADC_USDC_GAUGE),
        ("EUROC_USDC", addresses.DFX_EUROC_USDC_GAUGE),
        ("GYEN_USDC", addresses.DFX_GYEN_USDC_GAUGE),
        ("NZDS_USDC", addresses.DFX_NZDS_USDC_GAUGE),
        ("TRYB_USDC", addresses.DFX_TRYB_USDC_GAUGE),
        ("XIDR_USDC", addresses.DFX_XIDR_USDC_GAUGE),
        ("XSGD_USDC", addresses.DFX_XSGD_USDC_GAUGE),
    ]
    new_lp_addresses = [
        ("CADC_USDC", addresses.DFX_CADC_USDC_LP),
        ("EUROC_USDC", addresses.DFX_EUROC_USDC_LP),
        ("GYEN_USDC", addresses.DFX_GYEN_USDC_LP),
        ("NZDS_USDC", addresses.DFX_NZDS_USDC_LP),
        ("TRYB_USDC", addresses.DFX_TRYB_USDC_LP),
        ("XIDR_USDC", addresses.DFX_XIDR_USDC_LP),
        ("XSGD_USDC", addresses.DFX_XSGD_USDC_LP),
    ]

    # ON LOCAL NODE: Provide multisig with ether
    HARDHAT_ACCT.transfer(MULTISIG_ACCT, "5 ether", gas_price=gas_strategy, silent=True)

    # # Fastforward chain to current date and check how existing gauges behave
    # end_dt_0 = datetime(2022, 11, 22, 14, 5, 0, tzinfo=timezone.utc)
    # fastforward_chain(end_dt_0)
    # log_distributor_info()
    # log_gauges_info(existing_gauges)

    # ### Test if re-enabling distributions returns rewards as normal
    # end_dt_1 = datetime(2022, 11, 24, 0, 0, 30, tzinfo=timezone.utc)
    # fastforward_chain(end_dt_1)
    # log_distributor_info()
    # log_gauges_info(existing_gauges)

    # enable_distributions()
    # # enable_gauges(existing_gauges)
    # distribute_rewards(existing_gauges)
    # log_distributor_info()
    # log_gauges_info(existing_gauges)

    # end_dt_2 = datetime(2022, 11, 25, 1, 35, 40, tzinfo=timezone.utc)
    # fastforward_chain(end_dt_2)
    # update_epoch()
    # checkpoint_rewards()
    # log_distributor_info()
    # log_gauges_info(existing_gauges)

    # ### Test if 0ing weight during current epoch will disable rewards next distribution
    # end_dt_1 = datetime(2022, 11, 24, 0, 0, 30, tzinfo=timezone.utc)
    # fastforward_chain(end_dt_1)
    # enable_gauges(existing_gauges)
    # zero_existing_gauge_weights(existing_gauges)
    # distribute_rewards(existing_gauges)
    # log_distributor_info()
    # log_gauges_info(existing_gauges)

    # # Create new gauges for LP pools and add to GaugeController
    # end_dt_2 = datetime(2022, 11, 24, 0, 0, 30, tzinfo=timezone.utc)
    # fastforward_chain(end_dt_2)
    # log_gauge_weights(existing_gauges)
    # zero_existing_gauge_weights(existing_gauges)

    # end_dt_3 = datetime(2022, 11, 26, 0, 0, 30, tzinfo=timezone.utc)
    # fastforward_chain(end_dt_3)
    #####
    #####

    log_distributor_info()
    log_gauges_info(existing_gauges)

    new_gauges = deploy_proxied_gauges(new_lp_addresses)
    add_to_gauge_controller(new_gauges)

    enable_distributions()

    all_gauges = [("ORIG_" + label, addr) for label, addr in existing_gauges] + [
        ("NEW_" + label, addr) for label, addr in new_gauges
    ]
    end_dt_4 = datetime(2022, 12, 15, 0, 0, 30, tzinfo=timezone.utc)
    fastforward_chain(end_dt_4)
    distribute_rewards(new_gauges)
    # # update_epoch()
    log_distributor_info()
    log_gauges_info(all_gauges)


if __name__ == "__main__":
    main()
