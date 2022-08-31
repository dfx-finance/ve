#!/usr/bin/env python
import brownie
from brownie import accounts
import math

from scripts import addresses
from scripts.helper import get_json_address, load_dfx_token
from utils.apr import calc_boosted_apr


SECONDS_PER_YEAR = 365 * 24 * 60 * 60


def get_apr(dfx, voting_escrow, veboost_proxy, acct, gauge):
    apr = math.inf
    if gauge.totalSupply():
        available_rewards = dfx.balanceOf(gauge)
        apr = calc_boosted_apr(
            voting_escrow, veboost_proxy, gauge, acct, available_rewards)
    return apr


def main():
    acct = accounts[0]

    dfx_distributor_address = get_json_address(
        'deployed_distributor', ['distributor', 'proxy'])
    veboost_proxy_address = get_json_address(
        'deployed_gaugecontroller', ['veBoostProxy'])
    cadc_gauge_address = get_json_address(
        'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'CADC_USDC', 'proxy'])
    eurs_gauge_address = get_json_address(
        'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'EURS_USDC', 'proxy'])
    euroc_gauge_address = get_json_address(
        'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'EUROC_USDC', 'proxy'])
    nzds_gauge_address = get_json_address(
        'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'NZDS_USDC', 'proxy'])
    tryb_gauge_address = get_json_address(
        'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'TRYB_USDC', 'proxy'])
    xidr_gauge_address = get_json_address(
        'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'XIDR_USDC', 'proxy'])
    xsgd_gauge_address = get_json_address(
        'deployed_liquidity_gauges_v4', ['gauges', 'amm', 'XSGD_USDC', 'proxy'])

    dfx = load_dfx_token()
    distributor = brownie.interface.IDfxDistributor(dfx_distributor_address)
    voting_escrow = brownie.interface.IVotingEscrow(addresses.VOTE_ESCROW)
    veboost_proxy = brownie.interface.IVeBoostProxy(veboost_proxy_address)
    cadc_liquidity_gauge = brownie.interface.ILiquidityGauge(
        cadc_gauge_address)
    eurs_liquidity_gauge = brownie.interface.ILiquidityGauge(
        eurs_gauge_address)
    euroc_liquidity_gauge = brownie.interface.ILiquidityGauge(
        euroc_gauge_address)
    nzds_liquidity_gauge = brownie.interface.ILiquidityGauge(
        nzds_gauge_address)
    tryb_liquidity_gauge = brownie.interface.ILiquidityGauge(
        tryb_gauge_address)
    xidr_liquidity_gauge = brownie.interface.ILiquidityGauge(
        xidr_gauge_address)
    xsgd_liquidity_gauge = brownie.interface.ILiquidityGauge(
        xsgd_gauge_address)

    distributor_dfx_balance = dfx.balanceOf(dfx_distributor_address)
    rate = distributor.rate()

    gauges = [cadc_liquidity_gauge, eurs_liquidity_gauge, euroc_liquidity_gauge,
              nzds_liquidity_gauge, tryb_liquidity_gauge, xidr_liquidity_gauge, xsgd_liquidity_gauge]
    [cadc_usdc_apr, eurs_usdc_apr, euroc_usdc_apr, nzds_usdc_apr, tryb_usdc_apr,
        xidr_usdc_apr, xsgd_usdc_apr] = [get_apr(dfx, voting_escrow, veboost_proxy, acct, g) for g in gauges]

    print((
        f"Distributor mining epoch: {distributor.miningEpoch()}\n"
        f"Distributor balance (DFX): {dfx_distributor_address} ({distributor_dfx_balance / 1e18})\n"
        f"Distributor rate (DFX per second): {rate} ({rate / 1e18})\n"
        f"Distributor rate (DFX per year): {rate * SECONDS_PER_YEAR} ({rate * SECONDS_PER_YEAR / 1e18})\n"
        f"CADC/USDC APR: {(cadc_usdc_apr * 100):.2f}\n"
        f"EURS/USDC APR: {(eurs_usdc_apr * 100):.2f}\n"
        f"EUROC/USDC APR: {(euroc_usdc_apr * 100):.2f}\n"
        f"NZDS/USDC APR: {(nzds_usdc_apr * 100):.2f}\n"
        f"TRYB/USDC APR: {(tryb_usdc_apr * 100):.2f}\n"
        f"XIDR/USDC APR: {(xidr_usdc_apr * 100):.2f}\n"
        f"XSGD/USDC APR: {(xsgd_usdc_apr * 100):.2f}"
    ))


if __name__ == '__main__':
    pass
