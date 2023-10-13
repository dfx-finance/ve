#!/usr/bin/env python
import pytest
from brownie import ZERO_ADDRESS, Contract
from brownie.network import gas_price
from utils.gas import gas_strategy

from utils.chain import (
    fastforward_chain_weeks,
    # fastforward_chain_weeks_anvil as fastforward_chain_weeks,
)


@pytest.fixture(scope="function", autouse=True)
def setup_gas():
    gas_price(gas_strategy)


"""
Accounts
"""


# Default account to deploy all test contracts
@pytest.fixture(scope="function")
def deploy_account(accounts):
    yield accounts[0]


# Secondary account to deploy test upgradeable proxies
@pytest.fixture(scope="function")
def deploy_proxy_account(accounts):
    yield accounts[1]


# Primary account to emulate DAO multisig
@pytest.fixture(scope="function")
def multisig_0(accounts):
    yield accounts[2]


# Secondary account to emulate DAO multisig
@pytest.fixture(scope="function")
def multisig_1(accounts):
    yield accounts[3]


# Test user wallet 1
@pytest.fixture(scope="function")
def user_0(accounts):
    yield accounts[4]


# Test user wallet 2
@pytest.fixture(scope="function")
def user_1(accounts):
    yield accounts[5]


"""
Contracts
"""


# Native test token
@pytest.fixture(scope="function")
def DFX(DFX_, deploy_account):
    yield DFX_.deploy(1e30, {"from": deploy_account})


# Vote-escrow version of test token
@pytest.fixture(scope="function")
def veDFX(VeDFX, DFX, deploy_account):
    yield VeDFX.deploy(DFX, "veDFX", "veDFX", 1, {"from": deploy_account})


# Cross-chain version of test token
@pytest.fixture(scope="function")
def DFX_OFT(DFX_, deploy_account):
    yield DFX_.deploy(1e30, {"from": deploy_account})


# Vote-escrow controller which tracks the various gauges and their current votes
@pytest.fixture(scope="function")
def gauge_controller(GaugeController, DFX, veDFX, deploy_account, multisig_0):
    yield GaugeController.deploy(
        DFX,
        veDFX,
        multisig_0,
        {"from": deploy_account},
    )


# Vote-escrow balances of individual users
@pytest.fixture(scope="function")
def veboost_proxy(VeBoostProxy, veDFX, deploy_account, multisig_0):
    yield VeBoostProxy.deploy(
        veDFX,
        ZERO_ADDRESS,
        multisig_0,
        {"from": deploy_account},
    )


# Vote-escrow rewards contract which holds and distributes rewards weekly to registered
# active gauges depending on their weights registered on the GaugeController
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
    dfx_distributor = DfxDistributor.deploy({"from": deploy_account})

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
        {"from": deploy_account},
    )

    # Load Distributor ABI on proxy address
    dfx_distributor_proxy = Contract.from_abi(
        "DfxDistributor", proxy.address, DfxDistributor.abi
    )

    yield dfx_distributor_proxy


# Layer 2 distributor which receives rewards through CCIP router and distributes
# rewards linearly to a RewardsOnlyGauge. For each RewardsOnlyGauge, there is an
# associated ChildChainStreamer.
@pytest.fixture(scope="function")
def child_chain_streamer(
    DFX_OFT,
    ChildChainStreamerCctp,
    mock_ccip_router,
    child_gauge_L2,
    deploy_account,
    multisig_0,
):
    yield ChildChainStreamerCctp.deploy(
        multisig_0,
        child_gauge_L2,
        DFX_OFT,
        mock_ccip_router,
        {"from": deploy_account},
    )


# Test-only contract which mocks the Chainlink CCIP router
@pytest.fixture(scope="function")
def mock_ccip_router(DFX_OFT, MockCcipRouter, deploy_account):
    router = MockCcipRouter.deploy({"from": deploy_account})
    # give router some rewards to distribute to L2 ChildChainStreamer
    DFX_OFT.transfer(
        router,
        1e25,
        {"from": deploy_account},
    )
    yield router


"""
Gauges
"""


def _deploy_lpt(ERC20LP, name, symbol, deploy_account, decimals=18, amount=1e9):
    return ERC20LP.deploy(name, symbol, 18, 1e9, {"from": deploy_account})


def _deploy_gauge_L1(
    DFX,
    veDFX,
    LiquidityGaugeV4,
    DfxUpgradeableProxy,
    veboost_proxy,
    distributor,
    lp_token,
    deploy_account,
    multisig_0,
    multisig_1,
):
    # deploy gauge logic
    gauge = LiquidityGaugeV4.deploy({"from": deploy_account})

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
        {"from": deploy_account},
    )

    gauge_proxy = Contract.from_abi(
        "LiquidityGaugeV4", dfx_upgradeable_proxy, LiquidityGaugeV4.abi
    )
    return gauge_proxy


# Deploys an LPT as found on Layer 1
@pytest.fixture(scope="function")
def lpt_L1(ERC20LP, deploy_account):
    yield _deploy_lpt(ERC20LP, "L1 BTC/ETH LPT", deploy_account)


# Deploys a LiquidityGaugeV4 contract as found on Layer 1
@pytest.fixture(scope="function")
def gauge_L1(
    DFX,
    veDFX,
    LiquidityGaugeV4,
    DfxUpgradeableProxy,
    veboost_proxy,
    distributor,
    lpt_L1,
    deploy_account,
    multisig_0,
    multisig_1,
):
    gauge = _deploy_gauge_L1(
        DFX,
        veDFX,
        LiquidityGaugeV4,
        DfxUpgradeableProxy,
        veboost_proxy,
        distributor,
        lpt_L1,
        deploy_account,
        multisig_0,
        multisig_1,
    )

    return gauge


def _deploy_root_gauge_L1(
    DFX,
    RootGaugeCcip,
    DfxUpgradeableProxy,
    distributor,
    ccip_router,
    deploy_account,
    multisig_0,
    multisig_1,
):
    # deploy gauge logic
    gauge_implementation = RootGaugeCcip.deploy(
        DFX,
        {"from": deploy_account},
    )

    # deploy gauge proxy and initialize
    gauge_initializer_calldata = gauge_implementation.initialize.encode_input(
        "L1 ETH/BTC Root Gauge",
        distributor,
        ccip_router,  # mock ccip router address
        14767482510784806043,  # mock target chain selector
        "0x33Af579F8faFADa29d98922A825CFC0228D7ce39",  # mock destination address
        "0x0000000000000000000000000000000000000000",  # mock fee token address
        multisig_0,
    )
    proxy = DfxUpgradeableProxy.deploy(
        gauge_implementation.address,
        multisig_1,
        gauge_initializer_calldata,
        {"from": deploy_account},
    )

    # load gauge interface on proxy for non-admin users
    gauge_proxy = Contract.from_abi("RootGaugeCcip", proxy, RootGaugeCcip.abi)
    return gauge_proxy


def _deploy_child_gauge_L2(
    RewardsOnlyGauge,
    DfxUpgradeableProxy,
    lp_token,
    deploy_account,
    multisig_0,
    multisig_1,
):
    # deploy gauge logic
    gauge_implementation = RewardsOnlyGauge.deploy(
        {"from": deploy_account},
    )

    # deploy gauge proxy and initialize
    gauge_initializer_calldata = gauge_implementation.initialize.encode_input(
        multisig_0, lp_token
    )
    proxy = DfxUpgradeableProxy.deploy(
        gauge_implementation.address,
        multisig_1,
        gauge_initializer_calldata,
        {"from": deploy_account},
    )

    # load gauge interface on proxy for non-admin users
    gauge_proxy = Contract.from_abi("RewardsOnlyGauge", proxy, RewardsOnlyGauge.abi)
    return gauge_proxy


# Deploys a RootGaugeCcip on Layer 1, sends to a L2 RewardsOnlyGauge via ChildChainStreamer
@pytest.fixture(scope="function")
def root_gauge_L1(
    DFX,
    RootGaugeCcip,
    DfxUpgradeableProxy,
    distributor,
    mock_ccip_router,
    deploy_account,
    multisig_0,
    multisig_1,
):
    root_gauge = _deploy_root_gauge_L1(
        DFX,
        RootGaugeCcip,
        DfxUpgradeableProxy,
        distributor,
        mock_ccip_router,
        deploy_account,
        multisig_0,
        multisig_1,
    )
    return root_gauge


# Deploys an LPT as found on Layer 2
@pytest.fixture(scope="function")
def lpt_L2(ERC20LP, deploy_account):
    return _deploy_lpt(ERC20LP, "L2 BTC/ETH LPT", "l2-cadc-usdc-lpt", deploy_account)


# Deploys a RewardsOnlyGauge contract on Layer 2, receives from a L1 RootGaugeCcip via ChildChainStreamer
@pytest.fixture(scope="function")
def child_gauge_L2(
    RewardsOnlyGauge,
    DfxUpgradeableProxy,
    lpt_L2,
    deploy_account,
    multisig_0,
    multisig_1,
):
    child_gauge = _deploy_child_gauge_L2(
        RewardsOnlyGauge,
        DfxUpgradeableProxy,
        lpt_L2,
        deploy_account,
        multisig_0,
        multisig_1,
    )
    return child_gauge


###
### Real-world Emulation
###
# Deploys 3 LPTs to represent real-world pools
@pytest.fixture(scope="function")
def three_lpts(ERC20LP, deploy_account):
    test_lps = [
        ("DFX CADC-USDC LP Token", "cadcUsdc"),
        ("DFX EUROC-USDC LP Token", "eurocUsdc"),
        ("DFX XSGD-USDC LP Token", "xsgdUsdc"),
    ]

    lp_tokens = [
        _deploy_lpt(ERC20LP, name, symbol, deploy_account) for name, symbol in test_lps
    ]
    return lp_tokens


@pytest.fixture(scope="function")
def three_gauges_L1(
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
        gauge_proxy = _deploy_gauge_L1(
            DFX,
            veDFX,
            LiquidityGaugeV4,
            DfxUpgradeableProxy,
            veboost_proxy,
            distributor,
            lp_token,
            deploy_account,
            multisig_0,
            multisig_1,
        )
        contracts.append(gauge_proxy)
    yield contracts
