#!/usr/bin/env python
from datetime import datetime
import json
import os
import time

from brownie import chain, web3
from . import contracts
from .constants import SECONDS_PER_YEAR
from .network import get_network_addresses


### File
# Logs data to file
def write_json_log(base_fn: str, output_data: dict) -> str:
    fp = f"./scripts/{base_fn}_{int(time.time())}.json"
    with open(fp, "w") as output_f:
        json.dump(output_data, output_f, indent=4)
    return fp


# Writes contract name and address to a "latest" master list file or overwrites
def write_contract(label: str, address: str):
    fp = f"./scripts/ve-addresses-latest.json"
    data = {}
    if os.path.exists(fp):
        try:
            data = json.load(open(fp))
        except json.JSONDecodeError:
            pass
    data[label] = address
    with open(fp, "w") as json_f:
        json.dump(data, json_f, indent=4)


### Console
def log_distributor_info():
    _addresses = get_network_addresses()
    dfx = contracts.erc20(_addresses.DFX)
    dfx_distributor = contracts.dfx_distributor(_addresses.DFX_DISTRIBUTOR)

    block_num = web3.eth.block_number
    block_timestamp = chain[block_num]["timestamp"]

    rewards_enabled = "on" if dfx_distributor.distributionsOn() else "off"
    distributor_dfx_balance = dfx.balanceOf(dfx_distributor.address)
    rate = dfx_distributor.rate()

    print("--- Distributor Info -------------------------")
    print(
        f"Block time (UTC): {datetime.utcfromtimestamp(block_timestamp)} ({block_num})\n"
        f"Distributions: {rewards_enabled}\n"
        f"Distributor mining epoch: {dfx_distributor.miningEpoch()}\n"
        f"Distributor epoch start time: {datetime.fromtimestamp(dfx_distributor.startEpochTime())}\n"
        f"Distributor balance (DFX): {dfx_distributor.address} ({distributor_dfx_balance / 1e18})\n"
        f"Distributor rate (DFX per second): {rate} ({rate / 1e18})\n"
        f"Distributor rate (DFX per year): {rate * SECONDS_PER_YEAR} ({rate * SECONDS_PER_YEAR / 1e18})\n"
    )


def log_gauges_info(gauge_addresses):
    _addresses = get_network_addresses()
    dfx = contracts.erc20(_addresses.DFX)
    gauge_controller = contracts.gauge_controller(_addresses.GAUGE_CONTROLLER)

    print("--- Gauges Info -------------------------")
    weights = [gauge_controller.get_gauge_weight(addr) for _, addr in gauge_addresses]
    total_weight = sum(weights)
    for i, weight in enumerate(weights):
        label, addr = gauge_addresses[i]
        g = contracts.gauge(addr)
        raw_dfx_rate = g.reward_data(_addresses.DFX)[3]
        undistributed_dfx_rewards = (raw_dfx_rate * 604800) / 1e18
        rewards = [f"{undistributed_dfx_rewards} DFX"]
        dfx_balance = dfx.balanceOf(g) / 1e18

        weight_pct = weight / total_weight * 100 if total_weight else 0
        print(
            f"{label} gauge weight: {weight_pct:.2f}% ({(' / ').join(rewards)}) (DFX balance: {dfx_balance})"
        )
    print("")


def log_gauge_weights(gauge_addresses):
    _addresses = get_network_addresses()
    gauge_controller = contracts.gauge_controller(_addresses.GAUGE_CONTROLLER)

    print("--- Gauges Weights -------------------------")
    weights = [gauge_controller.get_gauge_weight(addr) for _, addr in gauge_addresses]
    for i, weight in enumerate(weights):
        label, _ = gauge_addresses[i]
        print(f"{label} gauge weight: {weight}")
