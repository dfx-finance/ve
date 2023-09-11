from brownie import Contract, Token, accounts

def main():
    _deploy_child_gauge_L2()




def _deploy_child_gauge_L2(
    RewardsOnlyGauge,
    DfxUpgradeableProxy,
    lp_token=0xFd57b4ddBf88a4e07fF4e34C487b99af2Fe82a05,
):
    acct = accounts.load('deployment_account')

    # deploy gauge logic
    gauge_implementation = RewardsOnlyGauge.deploy(
        {"from": acct},
    )

    # deploy gauge proxy and initialize
    gauge_initializer_calldata = gauge_implementation.initialize.encode_input(
        acct, lp_token
    )
    proxy = DfxUpgradeableProxy.deploy(
        gauge_implementation.address,
        acct,
        gauge_initializer_calldata,
        {"from": acct},
    )

    # load gauge interface on proxy for non-admin users
    gauge_proxy = Contract.from_abi("RewardsOnlyGauge", proxy, RewardsOnlyGauge.abi)
    return gauge_proxy