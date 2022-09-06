#!/usr/bin/env python
import brownie
from brownie import accounts
import math

from scripts import addresses, contracts
from scripts.helper import get_json_address, load_dfx_token
from utils.apr import calc_boosted_apr


SECONDS_PER_YEAR = 365 * 24 * 60 * 60
DEPLOY_ACCT = accounts.load('hardhat')


def get_apr(dfx, voting_escrow, veboost_proxy, acct, gauge):
    apr = math.inf
    if gauge.totalSupply():
        available_rewards = dfx.balanceOf(gauge)
        apr = calc_boosted_apr(
            voting_escrow, veboost_proxy, gauge, acct, available_rewards)
    return apr


def main():
    dfx_distributor = contracts.dfx_distributor()
    veboost_proxy = contracts.veboost_proxy()
    gauges = contracts.gauges()

    dfx = load_dfx_token()
    voting_escrow = brownie.interface.IVotingEscrow(addresses.VOTE_ESCROW)

    distributor_dfx_balance = dfx.balanceOf(dfx_distributor.address)
    rate = dfx_distributor.rate()

    [cadc_usdc_apr, eurs_usdc_apr, euroc_usdc_apr, nzds_usdc_apr, tryb_usdc_apr,
        xidr_usdc_apr, xsgd_usdc_apr] = [get_apr(dfx, voting_escrow, veboost_proxy, DEPLOY_ACCT, g) for g in gauges]

    print((
        f'Distributor mining epoch: {dfx_distributor.miningEpoch()}\n'
        f'Distributor balance (DFX): {dfx_distributor.address} ({distributor_dfx_balance / 1e18})\n'
        f'Distributor rate (DFX per second): {rate} ({rate / 1e18})\n'
        f'Distributor rate (DFX per year): {rate * SECONDS_PER_YEAR} ({rate * SECONDS_PER_YEAR / 1e18})'
    ))

    gauge_aprs = [get_apr(dfx, voting_escrow, veboost_proxy,
                          DEPLOY_ACCT, g) for g in gauges]
    for i, gauge_id in enumerate(contracts.GAUGE_IDS):
        label = gauge_id.replace('_', '/')
        print(f'{label}: {(gauge_aprs[i] * 100):.2f}')


if __name__ == '__main__':
    pass
