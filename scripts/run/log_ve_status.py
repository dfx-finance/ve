#!/usr/bin/env python
from brownie import accounts, chain, web3
from datetime import datetime
import math

from scripts import contracts
from scripts.helper import get_addresses, load_dfx_token
from utils.apr import calc_global_boosted_apr
from utils.constants import DFX_PRICE, LP_PRICE


SECONDS_PER_YEAR = 365 * 24 * 60 * 60
# DEPLOY_ACCT = accounts.load('hardhat')
DEPLOY_ACCT = accounts.load('deployve')

addresses = get_addresses()


# TODO: check this, seems to return APR for deploy acct as a user,
# should be returning a global (not tied to any particular account) APR
def get_gauge_info(dfx, gauge):
    apr = math.inf
    available_rewards = dfx.balanceOf(gauge)
    label = gauge.name()
    if gauge.totalSupply():
        apr = calc_global_boosted_apr(gauge, available_rewards)
    return label, available_rewards, apr


def main():
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)
    gauges = contracts.gauges()

    block_num = web3.eth.block_number
    block_timestamp = chain[block_num]['timestamp']

    dfx = load_dfx_token()

    rewards_enabled = 'on' if dfx_distributor.distributionsOn() else 'off'
    distributor_dfx_balance = dfx.balanceOf(dfx_distributor.address)
    rate = dfx_distributor.rate()

    print((
        f'Block time: {datetime.fromtimestamp(block_timestamp)}\n'
        f'Distributions: {rewards_enabled}\n'
        f'Distributor mining epoch: {dfx_distributor.miningEpoch()}\n'
        f'Distributor balance (DFX): {dfx_distributor.address} ({distributor_dfx_balance / 1e18})\n'
        f'Distributor rate (DFX per second): {rate} ({rate / 1e18})\n'
        f'Distributor rate (DFX per year): {rate * SECONDS_PER_YEAR} ({rate * SECONDS_PER_YEAR / 1e18})'
    ))

    gauge_infos = [get_gauge_info(dfx, g) for g in gauges]
    for label, rewards, apr in gauge_infos:
        print(f'{label}: {(apr * 100):.2f}% (Avail. rewards: {rewards / 1e18})')

    print(
        f'NOTE: DFX price (${DFX_PRICE}) and LPT price (${LP_PRICE}) are estimated and set as constants. APRs will be off accordingly.')


if __name__ == '__main__':
    pass
