#!/usr/bin/env python
from brownie import ZERO_ADDRESS, Contract, network
import json
import pytest

from utils.chain import fastforward_chain_weeks
from utils.gas import gas_strategy
from utils.network import network_info

connected = network_info()


@pytest.fixture(scope="session", autouse=True)
def set_gas_limit():
    network.gas_limit("auto")


"""
Accounts
"""


@pytest.fixture(scope="module")
def master_account(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def new_master_account(accounts):
    yield accounts[1]


@pytest.fixture(scope="module")
def user_accounts(accounts):
    yield accounts[2:5]


@pytest.fixture(scope="module")
def multisig_account(accounts):
    yield accounts[-1]


"""
Contracts
"""


@pytest.fixture(scope="module")
def dfx():
    # Load existing DFX ERC20 from mainnet fork
    abi = json.load(open("./tests/abis/Dfx.json"))
    yield Contract.from_abi("DFX", network.addresses.DFX, abi)


@pytest.fixture(scope="module")
def voting_escrow():
    # Load existing DFX ERC20 from mainnet fork
    abi = json.load(open("./tests/abis/veDfx.json"))
    yield Contract.from_abi("veDFX", network.addresses.VEDFX, abi)


@pytest.fixture(scope="module")
def mock_lp_tokens(ERC20LP, master_account):
    test_lps = [
        ("DFX CADC-USDC LP Token", "cadcUsdc"),
        ("DFX EUROC-USDC LP Token", "eurocUsdc"),
        ("DFX XSGD-USDC LP Token", "xsgdUsdc"),
    ]

    lp_tokens = [
        ERC20LP.deploy(
            name, symbol, 18, 1e9, {"from": master_account, "gas_price": gas_strategy}
        )
        for name, symbol in test_lps
    ]
    return lp_tokens


@pytest.fixture(scope="module")
def gauge_controller(GaugeController, dfx, voting_escrow, master_account):
    yield GaugeController.deploy(
        dfx,
        voting_escrow,
        master_account,
        {"from": master_account, "gas_price": gas_strategy},
    )


@pytest.fixture(scope="module")
def distributor(
    DfxDistributor,
    DfxUpgradeableProxy,
    gauge_controller,
    master_account,
    new_master_account,
):
    fastforward_chain_weeks(num_weeks=0, delta=0)

    # Deploy DfxDistributor logic
    dfx_distributor = DfxDistributor.deploy(
        {"from": master_account, "gas_price": gas_strategy}
    )

    # Deploy DfxDistributor proxy
    distributor_initializer_calldata = dfx_distributor.initialize.encode_input(
        network.addresses.DFX,
        gauge_controller,
        0,
        0,
        # should consider using another multisig to deal with access control
        new_master_account,
        network.addresses.DFX_MULTISIG_0,
        ZERO_ADDRESS,
    )
    proxy = DfxUpgradeableProxy.deploy(
        dfx_distributor.address,
        network.addresses.DFX_MULTISIG_0,
        distributor_initializer_calldata,
        {"from": master_account, "gas_price": gas_strategy},
    )

    # Load Distributor ABI on proxy address
    dfx_distributor_proxy = Contract.from_abi(
        "DfxDistributor", proxy.address, DfxDistributor.abi
    )

    yield dfx_distributor_proxy


@pytest.fixture(scope="module")
def veboost_proxy(VeBoostProxy, voting_escrow, master_account):
    yield VeBoostProxy.deploy(
        voting_escrow,
        ZERO_ADDRESS,
        master_account,
        {"from": master_account, "gas_price": gas_strategy},
    )


"""
Rewards & Gauges
"""


@pytest.fixture(scope="module")
def three_liquidity_gauges_v4(
    LiquidityGaugeV4,
    DfxUpgradeableProxy,
    mock_lp_tokens,
    veboost_proxy,
    distributor,
    master_account,
):
    contracts = []
    for lp_token in mock_lp_tokens:
        # deploy gauge logic
        gauge = LiquidityGaugeV4.deploy(
            {"from": master_account, "gas_price": gas_strategy}
        )

        # deploy gauge behind proxy
        gauge_initializer_calldata = gauge.initialize.encode_input(
            lp_token,
            network.addresses.DFX_MULTISIG_0,
            network.addresses.DFX,
            network.addresses.VEDFX,
            veboost_proxy,
            distributor,
        )
        dfx_upgradeable_proxy = DfxUpgradeableProxy.deploy(
            gauge.address,
            network.addresses.DFX_MULTISIG_0,
            gauge_initializer_calldata,
            {"from": master_account, "gas_price": gas_strategy},
        )

        gauge_proxy = Contract.from_abi(
            "LiquidityGaugeV4", dfx_upgradeable_proxy, LiquidityGaugeV4.abi
        )
        contracts.append(gauge_proxy)
    yield contracts
