#!/usr/bin/env python
import brownie

from scripts import contracts
from scripts.helper import gas_strategy, get_addresses, DEPLOY_ACCT, PROXY_MULTISIG


addresses = get_addresses()

NEW_ADMIN_MULTISIG = "0x27E843260c71443b4CC8cB6bF226C3f77b9695AF"
NEW_GOVERNOR_MULTISIG = NEW_ADMIN_MULTISIG
NEW_GUARDIAN_MULTISIG = NEW_ADMIN_MULTISIG
NEW_PROXY_MULTISIG = "0x26f539A0fE189A7f228D7982BF10Bc294FA9070c"


def transfer_veboost_admin(orig_addr, new_addr):
    veboost_proxy = contracts.veboost_proxy(addresses.VOTE_ESCROW)
    # veboost_proxy.commit_admin(
    #     new_addr, {'from': orig_addr, 'gas_price': gas_strategy})
    # veboost_proxy.accept_transfer_ownership(
    #     {'from': new_addr, 'gas_price': gas_strategy})
    print(f"VeBoostProxy transfer success: {veboost_proxy.admin() == new_addr}")


def transfer_gauge_controller_admin(orig_addr, new_addr):
    print(addresses.DFX_DISTRIBUTOR)
    gauge_controller = contracts.gauge_controller(addresses.DFX_DISTRIBUTOR)
    gauge_controller.commit_transfer_ownership(
        new_addr, {"from": orig_addr, "gas_price": gas_strategy}
    )
    # gauge_controller.accept_transfer_ownership(
    #     {'from': new_addr, 'gas_price': gas_strategy})
    # print(
    #     f"GaugeController transfer success: {gauge_controller.admin() == new_addr}")


def transfer_distributor_governor(orig_addr, new_addr):
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)
    governor_role = dfx_distributor.GOVERNOR_ROLE()
    print("gov", governor_role)
    # dfx_distributor.grantRole(governor_role, new_addr, {
    #                           'from': orig_addr, 'gas_price': gas_strategy})
    # dfx_distributor.renounceRole(governor_role, orig_addr, {
    #                              'from': orig_addr, 'gas_price': gas_strategy})
    # role_transferred = dfx_distributor.hasRole(
    #     governor_role, orig_addr) == False and dfx_distributor.hasRole(governor_role, new_addr) == True
    # print(f"DfxDistributor governor transfer success: {role_transferred}")


def transfer_distributor_guardian(orig_addr, new_addr):
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)
    guardian_role = dfx_distributor.GUARDIAN_ROLE()
    print("guard", guardian_role)
    # dfx_distributor.grantRole(guardian_role, new_addr, {
    #                           'from': orig_addr, 'gas_price': gas_strategy})
    # dfx_distributor.renounceRole(guardian_role, orig_addr, {
    #                              'from': orig_addr, 'gas_price': gas_strategy})
    # role_transferred = dfx_distributor.hasRole(
    #     guardian_role, orig_addr) == False and dfx_distributor.hasRole(guardian_role, new_addr) == True
    # print(f"DfxDistributor guardian transfer success: {role_transferred}")


def transfer_liquidity_gauge_v4(gauge_addr, orig_addr, new_addr):
    gauge = contracts.gauge(gauge_addr)
    gauge.commit_transfer_ownership(
        new_addr, {"from": orig_addr, "gas_price": gas_strategy}
    )
    # gauge.accept_transfer_ownership(
    #     {'from': new_addr, 'gas_price': gas_strategy})
    # print(f'{gauge.name()} LiquidityGaugeV4 transfer success: {gauge.admin() == new_addr}')


def transfer_all_liquidity_gauges(orig_addr, new_addr):
    for gauge_addr in contracts.GAUGE_ADDRESSES:
        transfer_liquidity_gauge_v4(gauge_addr, orig_addr, new_addr)


def transfer_distributor_proxy(orig_addr, new_addr):
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)
    upgradeable_proxy = brownie.interface.IDfxUpgradeableProxy(dfx_distributor.address)
    upgradeable_proxy.changeAdmin(
        new_addr, {"from": orig_addr, "gas_price": gas_strategy}
    )
    print(
        f"Distributor upgradeable proxy transfer success: {upgradeable_proxy.admin({'from': new_addr}) == new_addr}"
    )


def transfer_liquidity_gauge_v4_proxy(gauge_addr, orig_addr, new_addr):
    gauge = contracts.gauge(gauge_addr)
    upgradeable_proxy = brownie.interface.IDfxUpgradeableProxy(gauge.address)
    upgradeable_proxy.changeAdmin(
        new_addr, {"from": orig_addr, "gas_price": gas_strategy}
    )
    print(
        f"{gauge_addr} LiquidityGaugeV4 upgradeable proxy transfer success: {upgradeable_proxy.admin({'from': new_addr}) == new_addr}"
    )


def transfer_all_gauge_proxies(orig_addr, new_addr):
    for gauge_addr in contracts.GAUGE_ADDRESSES:
        transfer_liquidity_gauge_v4_proxy(gauge_addr, orig_addr, new_addr)


def main():
    print("Transfer contract admins...")
    transfer_veboost_admin(DEPLOY_ACCT, NEW_ADMIN_MULTISIG)
    transfer_gauge_controller_admin(DEPLOY_ACCT, NEW_ADMIN_MULTISIG)
    # guardian must be migrated first, then governor
    transfer_distributor_guardian(DEPLOY_ACCT, NEW_GUARDIAN_MULTISIG)
    transfer_distributor_governor(DEPLOY_ACCT, NEW_GOVERNOR_MULTISIG)
    transfer_all_liquidity_gauges(DEPLOY_ACCT, NEW_ADMIN_MULTISIG)

    print("Transfer upgradeable proxy admins...")
    transfer_distributor_proxy(PROXY_MULTISIG, NEW_PROXY_MULTISIG)
    transfer_all_gauge_proxies(PROXY_MULTISIG, NEW_PROXY_MULTISIG)


if __name__ == "__main__":
    main()
