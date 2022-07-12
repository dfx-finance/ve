from doctest import master
from brownie import ZERO_ADDRESS, Contract, network
import brownie
from brownie.network.gas.strategies import LinearScalingStrategy
import json
import pytest

import addresses

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('40 gwei', '150 gwei', 1.3)

'''
Accounts
'''


@pytest.fixture(scope='module')
def master_account(accounts):
    yield accounts[0]


@pytest.fixture(scope='module')
def new_master_account(accounts):
    yield accounts[1]


@pytest.fixture(scope='module')
def user_accounts(accounts):
    yield accounts[2:5]


'''
Contracts
'''


@pytest.fixture(scope='module')
def dfx():
    # Load existing DFX ERC20 from mainnet fork
    abi = json.load(open('./tests/abis/Dfx.json'))
    yield Contract.from_abi('DFX', addresses.DFX, abi)


@pytest.fixture(scope='module')
def voting_escrow():
    # Load existing DFX ERC20 from mainnet fork
    abi = json.load(open('./tests/abis/veDfx.json'))
    yield Contract.from_abi('veDFX', addresses.veDFX, abi)


@pytest.fixture(scope='module')
def mock_lp_token(ERC20LP, master_account):
    # NOTE: Why does Curve.fi use 1e9 here?
    yield ERC20LP.deploy('Curve LP Token', 'usdCrv', 18, 1e9, {'from': master_account, 'gas_price': gas_strategy})


@pytest.fixture(scope='module')
def mock_lp_tokens(ERC20LP, master_account):
    test_lps = [
        ('DFX CADC-USDC LP Token', 'cadcUsdc'),
        ('DFX EURS-USDC LP Token', 'eursUsdc'),
        ('DFX XSGD-USDC LP Token', 'xsgdUsdc'),
    ]
    lp_tokens = [
        ERC20LP.deploy(name, symbol, 18, 1e9, {
                       'from': master_account, 'gas_price': gas_strategy})
        for name, symbol in test_lps
    ]
    return lp_tokens


@pytest.fixture(scope='module')
def gauge_controller(GaugeController, dfx, voting_escrow, master_account):
    network.gas_limit('auto')
    yield GaugeController.deploy(dfx, voting_escrow, master_account, {'from': master_account, 'gas_price': gas_strategy})

@pytest.fixture(scope='module')
def veboost_proxy(VeBoostProxy, voting_escrow, master_account):
    yield VeBoostProxy.deploy(voting_escrow, ZERO_ADDRESS, master_account, {'from': master_account, 'gas_price': gas_strategy})


'''
Rewards & Gauges
'''

@pytest.fixture(scope='module')
def three_staking_rewards(StakingRewards, dfx, mock_lp_tokens, master_account):
    contracts = [
        StakingRewards.deploy(
            dfx, lp_token, {'from': master_account, 'gas_price': gas_strategy})
        for lp_token in mock_lp_tokens
    ]
    yield contracts


@pytest.fixture(scope='module')
def three_rewards_only_gauges(RewardsOnlyGauge, mock_lp_tokens, master_account):
    contracts = [
        RewardsOnlyGauge.deploy(master_account, lp_token, {
                                'from': master_account, 'gas_price': gas_strategy})
        for lp_token in mock_lp_tokens
    ]
    yield contracts

@pytest.fixture(scope='module')
def three_liquidity_gauges_v4(LiquidityGaugeV4, DfxUpgradableProxy, dfx, voting_escrow, mock_lp_tokens, veboost_proxy, dfx_distributor, master_account):
    contracts = []
    for curr_mock_lp_token in mock_lp_tokens:
        liquidity_gauges_logic = LiquidityGaugeV4.deploy({'from': master_account, 'gas_price': gas_strategy})

        liquidity_initializer_calldata = liquidity_gauges_logic.initialize.encode_input(
            curr_mock_lp_token,
            master_account,
            dfx,
            voting_escrow,
            veboost_proxy,
            dfx_distributor
        )   

        liquidity_gauges_proxy = DfxUpgradableProxy.deploy(
            liquidity_gauges_logic.address,
            master_account,
            liquidity_initializer_calldata,
            {"from": master_account, "gas_price": gas_strategy}
        )

        contracts.append(Contract.from_abi("LiquidityGaugeV4", liquidity_gauges_proxy.address, LiquidityGaugeV4.abi))
    yield contracts

@pytest.fixture(scope='module')
def dfx_distributor(DfxDistributor, DfxUpgradableProxy, dfx, gauge_controller, master_account):
    # deploy distributor first
    initial_rate = 1
    start_epoch_supply = 0

    distributor_logic = DfxDistributor.deploy({'from': master_account, 'gas_price': gas_strategy})

    distributor_initializer_calldata = distributor_logic.initialize.encode_input(
        dfx,
        gauge_controller,
        initial_rate,
        start_epoch_supply,
        master_account, # should consider using another multisig to deal with access control
        master_account, 
        ZERO_ADDRESS
    )
        
    distributor_proxy = DfxUpgradableProxy.deploy(
        distributor_logic.address,
        master_account,
        distributor_initializer_calldata,
        {"from": master_account, "gas_price": gas_strategy}
    )

    distributor = Contract.from_abi("DfxDistributor", distributor_proxy.address, DfxDistributor.abi)
    yield distributor