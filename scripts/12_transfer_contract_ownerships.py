#!/usr/bin/env python
import brownie
from brownie import accounts
from brownie.network import gas_price

from scripts.helper import gas_strategy, get_json_address

DEPLOY_ACCT = accounts.load('hardhat')
NEW_MULTISIG_ADDRESS = accounts[9]

gas_price(gas_strategy)


def transfer_veboost_proxy(orig_addr, new_addr):
    ve_boost_proxy_address = get_json_address(
        'deployed_gaugecontroller', ['veBoostProxy'])
    veboost_proxy = brownie.interface.IVeBoostProxy(ve_boost_proxy_address)
    veboost_proxy.commit_admin(
        new_addr, {'from': orig_addr, 'gas_price': gas_strategy})
    veboost_proxy.accept_transfer_ownership(
        {'from': new_addr, 'gas_price': gas_strategy})
    print(
        f"VeBoostProxy transfer success: {veboost_proxy.admin() == new_addr}")


def transfer_gauge_controller(orig_addr, new_addr):
    gauge_controller_address = get_json_address(
        'deployed_gaugecontroller', ['gaugeController'])
    gauge_controller = brownie.interface.IGaugeController(
        gauge_controller_address)
    gauge_controller.commit_transfer_ownership(
        new_addr, {'from': orig_addr, 'gas_price': gas_strategy})
    gauge_controller.accept_transfer_ownership(
        {'from': new_addr, 'gas_price': gas_strategy})
    print(
        f"GaugeController transfer success: {gauge_controller.admin() == new_addr}")


def main():
    print('Transfer contracts...')
    transfer_veboost_proxy(DEPLOY_ACCT, NEW_MULTISIG_ADDRESS)
    transfer_gauge_controller(DEPLOY_ACCT, NEW_MULTISIG_ADDRESS)


if __name__ == '__main__':
    main()
