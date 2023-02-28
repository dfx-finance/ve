#!/usr/bin/env python
from brownie import chain, web3
from datetime import datetime
import math

from scripts import contracts
from scripts.helper import get_addresses, load_dfx_token
from utils.apr import calc_global_boosted_apr
from utils.constants import DFX_PRICE, LP_PRICE


SECONDS_PER_YEAR = 365 * 24 * 60 * 60

addresses = get_addresses()


class GaugeInfo:
    apr: float = None
    label: str = None
    lpt_price: float = None
    reward_price: int = None
    total_lpt: int = None
    total_rewards: int = None
    weight: int = None


# fetch all gauge addresses which are not flagged as a killedGauge
def active_gauges(gauge_controller, dfx_distributor):
    num_gauges = gauge_controller.n_gauges()
    all_gauge_addresses = [gauge_controller.gauges(i) for i in range(0, num_gauges)]
    gauge_addresses = []
    for addr in all_gauge_addresses:
        print(addr, dfx_distributor.killedGauges(addr))
        if dfx_distributor.killedGauges(addr) == False:
            gauge_addresses.append(addr)
    return gauge_addresses


# TODO: implement calculating LPT price
def lpt_price(gauge):
    # lpt_addr = gauge.staking_token()
    # lpt = contracts.dfx_curve(lpt_addr)
    # underlying_0, underlying_1 = lpt.numeraires(0), lpt.numeraires(1)
    print(f"{gauge.name()} ({gauge.address})")
    # base = contracts.erc20(underlying_0)


# create object containing a variety of gauge stats
def get_gauge_info(dfx, gauge) -> GaugeInfo:
    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)
    info = GaugeInfo()
    info.total_rewards = dfx.balanceOf(gauge)
    info.label = gauge.name()
    info.total_lpt = gauge.totalSupply()
    info.lpt_price = lpt_price(gauge)
    info.reward_price = None
    info.apr = math.inf
    if info.total_lpt:
        info.apr = calc_global_boosted_apr(gauge, info.total_rewards)
    info.weight = gauge_controller.gauge_relative_weight(gauge.address)
    return info


def main():
    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    # Fetch enabled gauge addresses
    gauge_addresses = active_gauges(gauge_controller, dfx_distributor)
    gauges = [contracts.gauge(addr) for addr in gauge_addresses]

    block_num = web3.eth.block_number
    block_timestamp = chain[block_num]["timestamp"]

    dfx = load_dfx_token()

    rewards_enabled = "on" if dfx_distributor.distributionsOn() else "off"
    distributor_dfx_balance = dfx.balanceOf(dfx_distributor.address)
    rate = dfx_distributor.rate()

    print(
        (
            f"Block time (UTC): {datetime.utcfromtimestamp(block_timestamp)}\n"
            f"Distributions: {rewards_enabled}\n"
            f"Distributor mining epoch: {dfx_distributor.miningEpoch()}\n"
            f"Distributor epoch start time: {datetime.fromtimestamp(dfx_distributor.startEpochTime())}\n"
            f"Distributor balance (DFX): {dfx_distributor.address} ({distributor_dfx_balance / 1e18})\n"
            f"Distributor rate (DFX per second): {rate} ({rate / 1e18})\n"
            f"Distributor rate (DFX per year): {rate * SECONDS_PER_YEAR} ({rate * SECONDS_PER_YEAR / 1e18})"
        )
    )

    gauge_infos = [get_gauge_info(dfx, g) for g in gauges]
    for info in gauge_infos:
        print(
            f"{info.label}: Supply: {info.total_lpt / 1e18} -- APR: {(info.apr * 100):.2f}% (Avail. rewards: {info.total_rewards / 1e18}) | Weight: {info.weight}"
        )

    print(
        f"NOTE: DFX price (${DFX_PRICE}) and LPT price (${LP_PRICE}) are estimated and set as constants. APRs will be off accordingly."
    )


if __name__ == "__main__":
    pass
