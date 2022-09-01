#!/usr/bin/env python
import brownie
from brownie import accounts
from brownie.network import gas_price

from scripts import addresses
from scripts.helper import gas_strategy, get_json_address

DEPLOY_ACCT = accounts.load('hardhat')
PROXY_MULTISIG = accounts[7]
NEW_PROXY_MULTISIG = accounts[8]
NEW_ADMIN_MULTISIG = accounts[9]
NEW_GOVERNOR_MULTISIG = NEW_ADMIN_MULTISIG
NEW_GUARDIAN_MULTISIG = NEW_ADMIN_MULTISIG
# NEW_MULTISIG = addresses.DFX_MULTISIG
# NEW_GOVERNOR_MULTISIG = addresses.DFX_MULTISIG
# NEW_GUARDIAN_MULTISIG = addresses.DFX_MULTISIG

gas_price(gas_strategy)


def transfer_veboost_admin(orig_addr, new_addr):
    ve_boost_proxy_address = get_json_address(
        'deployed_gaugecontroller', ['veBoostProxy'])
    veboost_proxy = brownie.interface.IVeBoostProxy(ve_boost_proxy_address)
    veboost_proxy.commit_admin(
        new_addr, {'from': orig_addr, 'gas_price': gas_strategy})
    veboost_proxy.accept_transfer_ownership(
        {'from': new_addr, 'gas_price': gas_strategy})
    print(
        f"VeBoostProxy transfer success: {veboost_proxy.admin() == new_addr}")


def transfer_gauge_controller_admin(orig_addr, new_addr):
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


def transfer_distributor_governor(orig_addr, new_addr):
    dfx_distributor_address = get_json_address(
        'deployed_distributor', ['distributor', 'proxy'])
    dfx_distributor = brownie.interface.IDfxDistributor(
        dfx_distributor_address)
    governor_role = dfx_distributor.GOVERNOR_ROLE()
    dfx_distributor.grantRole(governor_role, new_addr, {
                              'from': orig_addr, 'gas_price': gas_strategy})
    dfx_distributor.renounceRole(governor_role, orig_addr, {
                                 'from': orig_addr, 'gas_price': gas_strategy})
    role_transferred = dfx_distributor.hasRole(
        governor_role, orig_addr) == False and dfx_distributor.hasRole(governor_role, new_addr) == True
    print(f"DfxDistributor governor transfer success: {role_transferred}")


def transfer_distributor_guardian(orig_addr, new_addr):
    dfx_distributor_address = get_json_address(
        'deployed_distributor', ['distributor', 'proxy'])
    dfx_distributor = brownie.interface.IDfxDistributor(
        dfx_distributor_address)
    guardian_role = dfx_distributor.GUARDIAN_ROLE()
    dfx_distributor.grantRole(guardian_role, new_addr, {
                              'from': orig_addr, 'gas_price': gas_strategy})
    dfx_distributor.renounceRole(guardian_role, orig_addr, {
                                 'from': orig_addr, 'gas_price': gas_strategy})
    role_transferred = dfx_distributor.hasRole(
        guardian_role, orig_addr) == False and dfx_distributor.hasRole(guardian_role, new_addr) == True
    print(f"DfxDistributor guardian transfer success: {role_transferred}")


def transfer_liquidity_gauge_v4(gauge_id, orig_addr, new_addr):
    gauge_addr = get_json_address('deployed_liquidity_gauges_v4', [
        'gauges', 'amm', gauge_id, 'proxy'])
    gauge = brownie.interface.ILiquidityGauge(gauge_addr)
    gauge.commit_transfer_ownership(
        new_addr, {'from': orig_addr, 'gas_price': gas_strategy})
    gauge.accept_transfer_ownership(
        {'from': new_addr, 'gas_price': gas_strategy})
    print(f'{gauge_id} LiquidityGaugeV4 transfer success: {gauge.admin() == new_addr}')


def transfer_all_liquidity_gauges(orig_addr, new_addr):
    gauge_ids = ['CADC_USDC', 'EURS_USDC', 'EUROC_USDC',
                 'NZDS_USDC', 'TRYB_USDC', 'XIDR_USDC', 'XSGD_USDC']
    for gauge_id in gauge_ids:
        transfer_liquidity_gauge_v4(gauge_id, orig_addr, new_addr)


def transfer_distributor_proxy(orig_addr, new_addr):
    dfx_distributor_address = get_json_address(
        'deployed_distributor', ['distributor', 'proxy'])
    upgradeable_proxy = brownie.interface.IDfxUpgradeableProxy(
        dfx_distributor_address)
    upgradeable_proxy.changeAdmin(
        new_addr, {'from': orig_addr, 'gas_price': gas_strategy})
    print(
        f"Distributor upgradeable proxy transfer success: {upgradeable_proxy.admin({'from': new_addr}) == new_addr}")


def transfer_liquidity_gauge_v4_proxy(gauge_id, orig_addr, new_addr):
    gauge_addr = get_json_address('deployed_liquidity_gauges_v4', [
        'gauges', 'amm', gauge_id, 'proxy'])
    upgradeable_proxy = brownie.interface.IDfxUpgradeableProxy(gauge_addr)
    upgradeable_proxy.changeAdmin(
        new_addr, {'from': orig_addr, 'gas_price': gas_strategy})
    print(
        f"{gauge_id} LiquidityGaugeV4 upgradeable proxy transfer success: {upgradeable_proxy.admin({'from': new_addr}) == new_addr}")


def transfer_all_gauge_proxies(orig_addr, new_addr):
    gauge_ids = ['CADC_USDC', 'EURS_USDC', 'EUROC_USDC',
                 'NZDS_USDC', 'TRYB_USDC', 'XIDR_USDC', 'XSGD_USDC']
    for gauge_id in gauge_ids:
        transfer_liquidity_gauge_v4_proxy(gauge_id, orig_addr, new_addr)


def main():
    print('Transfer contract admins...')
    transfer_veboost_admin(DEPLOY_ACCT, NEW_ADMIN_MULTISIG)
    transfer_gauge_controller_admin(DEPLOY_ACCT, NEW_ADMIN_MULTISIG)
    # guardian must be migrated first, then governor
    transfer_distributor_guardian(DEPLOY_ACCT, NEW_GUARDIAN_MULTISIG)
    transfer_distributor_governor(DEPLOY_ACCT, NEW_GOVERNOR_MULTISIG)
    transfer_all_liquidity_gauges(DEPLOY_ACCT, NEW_ADMIN_MULTISIG)

    print('Transfer upgradeable proxy admins...')
    transfer_distributor_proxy(PROXY_MULTISIG, NEW_PROXY_MULTISIG)
    transfer_all_gauge_proxies(PROXY_MULTISIG, NEW_PROXY_MULTISIG)


if __name__ == '__main__':
    main()
