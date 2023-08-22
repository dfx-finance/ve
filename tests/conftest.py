#!/usr/bin/env python
import pytest
from brownie import ZERO_ADDRESS, Contract

from utils.gas import gas_strategy
from utils.chain import (
    fastforward_chain_weeks,
    # fastforward_chain_weeks_anvil as fastforward_chain_weeks,
)


"""
Accounts
"""


@pytest.fixture(scope="function")
def deploy_account(accounts):
    yield accounts[0]


@pytest.fixture(scope="function")
def deploy_proxy_account(accounts):
    yield accounts[1]


@pytest.fixture(scope="function")
def multisig_0(accounts):
    yield accounts[2]


@pytest.fixture(scope="function")
def multisig_1(accounts):
    yield accounts[3]


@pytest.fixture(scope="function")
def user_0(accounts):
    yield accounts[4]


@pytest.fixture(scope="function")
def user_1(accounts):
    yield accounts[5]


"""
Contracts
"""


@pytest.fixture(scope="function")
def DFX(DFX_, deploy_account):
    yield DFX_.deploy(
        1000000 * 1e18, {"from": deploy_account, "gas_price": gas_strategy}
    )


@pytest.fixture(scope="function")
def veDFX(VeDFX, DFX, deploy_account):
    yield VeDFX.deploy(
        DFX, "veDFX", "veDFX", 1, {"from": deploy_account, "gas_price": gas_strategy}
    )


@pytest.fixture(scope="function")
def DFX_OFT(DFX_, deploy_account):
    yield DFX_.deploy(
        1000000 * 1e18, {"from": deploy_account, "gas_price": gas_strategy}
    )

@pytest.fixture(scope="function")
def DFXTokenTransfer(DFXTokenTransfer, deploy_account):
    yield DFXTokenTransfer.deploy(
      "0xD0daae2231E9CB96b94C8512223533293C3693Bf", "0x779877A7B0D9E8603169DdbD7836e478b4624789", {"from": deploy_account, "gas_price": gas_strategy}
    )



@pytest.fixture(scope="function")
def three_lpts(ERC20LP, deploy_account):
    test_lps = [
        ("DFX CADC-USDC LP Token", "cadcUsdc"),
        ("DFX EUROC-USDC LP Token", "eurocUsdc"),
        ("DFX XSGD-USDC LP Token", "xsgdUsdc"),
    ]

    lp_tokens = [
        ERC20LP.deploy(
            name, symbol, 18, 1e9, {"from": deploy_account, "gas_price": gas_strategy}
        )
        for name, symbol in test_lps
    ]
    return lp_tokens


@pytest.fixture(scope="function")
def gauge_controller(GaugeController, DFX, veDFX, deploy_account, multisig_0):
    yield GaugeController.deploy(
        DFX,
        veDFX,
        multisig_0,
        {"from": deploy_account, "gas_price": gas_strategy},
    )


@pytest.fixture(scope="function")
def veboost_proxy(VeBoostProxy, veDFX, deploy_account, multisig_0):
    yield VeBoostProxy.deploy(
        veDFX,
        ZERO_ADDRESS,
        multisig_0,
        {"from": deploy_account, "gas_price": gas_strategy},
    )


@pytest.fixture(scope="function")
def distributor(
    DFX,
    DfxDistributor,
    DfxUpgradeableProxy,
    gauge_controller,
    deploy_account,
    multisig_0,
    multisig_1,
):
    # deploy distributor as close to start of epoch as possible
    fastforward_chain_weeks(num_weeks=0, delta=0)

    # Deploy DfxDistributor logic
    dfx_distributor = DfxDistributor.deploy(
        {"from": deploy_account, "gas_price": gas_strategy}
    )

    # Deploy DfxDistributor proxy
    distributor_initializer_calldata = dfx_distributor.initialize.encode_input(
        DFX,
        gauge_controller,
        0,
        0,
        # should consider using another multisig to deal with access control
        multisig_0,
        multisig_0,
        ZERO_ADDRESS,
    )
    proxy = DfxUpgradeableProxy.deploy(
        dfx_distributor.address,
        multisig_1,
        distributor_initializer_calldata,
        {"from": deploy_account, "gas_price": gas_strategy},
    )

    # Load Distributor ABI on proxy address
    dfx_distributor_proxy = Contract.from_abi(
        "DfxDistributor", proxy.address, DfxDistributor.abi
    )

    yield dfx_distributor_proxy


"""
Gauges
"""


@pytest.fixture(scope="function")
def three_gauges(
    DFX,
    veDFX,
    LiquidityGaugeV4,
    DfxUpgradeableProxy,
    three_lpts,
    veboost_proxy,
    distributor,
    deploy_account,
    multisig_0,
    multisig_1,
):
    contracts = []
    for lp_token in three_lpts:
        # deploy gauge logic
        gauge = LiquidityGaugeV4.deploy(
            {"from": deploy_account, "gas_price": gas_strategy}
        )

        # deploy gauge behind proxy
        gauge_initializer_calldata = gauge.initialize.encode_input(
            lp_token,
            multisig_0,
            DFX,
            veDFX,
            veboost_proxy,
            distributor,
        )
        dfx_upgradeable_proxy = DfxUpgradeableProxy.deploy(
            gauge.address,
            multisig_1,
            gauge_initializer_calldata,
            {"from": deploy_account, "gas_price": gas_strategy},
        )

        gauge_proxy = Contract.from_abi(
            "LiquidityGaugeV4", dfx_upgradeable_proxy, LiquidityGaugeV4.abi
        )
        contracts.append(gauge_proxy)
    yield contracts
