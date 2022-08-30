#!/usr/bin/env python
import brownie
from brownie import accounts
import math

from scripts import addresses
from scripts.helper import get_json_address, load_dfx_token
from utils.apr import calc_boosted_apr


SECONDS_PER_YEAR = 365 * 24 * 60 * 60


def main():
    acct = accounts[0]

    dfx_distributor_address = get_json_address(
        'deployed_distributor', ['distributor', 'proxy'])
    veboost_proxy_address = get_json_address(
        'deployed_gaugecontroller', ['veBoostProxy'])
    cadc_gauge_address = get_json_address(
        'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'CADC_USDC', 'proxy'])

    dfx = load_dfx_token()
    distributor = brownie.interface.IDfxDistributor(dfx_distributor_address)
    voting_escrow = brownie.interface.IVotingEscrow(addresses.VOTE_ESCROW)
    veboost_proxy = brownie.interface.IVeBoostProxy(veboost_proxy_address)
    cadc_liquidity_gauge = brownie.interface.ILiquidityGauge(
        cadc_gauge_address)

    distributor_dfx_balance = dfx.balanceOf(dfx_distributor_address)
    rate = distributor.rate()

    apr = math.inf
    if cadc_liquidity_gauge.totalSupply():
        available_rewards = dfx.balanceOf(cadc_liquidity_gauge)
        apr = calc_boosted_apr(
            voting_escrow, veboost_proxy, cadc_liquidity_gauge, acct, available_rewards)

    print((
        "Status:\n"
        "-------\n"
        f"Distributor mining epoch: {distributor.miningEpoch()}\n"
        f"Distributor balance (DFX): {dfx_distributor_address} ({distributor_dfx_balance / 1e18})\n"
        f"Distributor rate (DFX per second): {rate} ({rate / 1e18})\n"
        f"Distributor rate (DFX per year): {rate * SECONDS_PER_YEAR} ({rate * SECONDS_PER_YEAR / 1e18})\n"
        f"CADC/USDC APR: {(apr * 100):.2f}"
    ))


if __name__ == '__main__':
    pass
