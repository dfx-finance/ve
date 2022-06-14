from brownie import Contract
from brownie.network.gas.strategies import LinearScalingStrategy
import json
import pytest

import addresses

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('60 gwei', '150 gwei', 1.3)

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
def voting_escrow(VotingEscrow, accounts, dfx):
    # Load existing DFX ERC20 from mainnet fork
    abi = json.load(open('./tests/abis/veDfx.json'))
    yield Contract.from_abi('veDFX', addresses.veDFX, abi)


@pytest.fixture(scope='module')
def mock_lp_token(ERC20LP, master_account):
    yield ERC20LP.deploy('Curve LP Token', 'usdCrv', 18, 10 ** 9, {'from': master_account, 'gas_price': gas_strategy})


@pytest.fixture(scope='module')
def gauge_controller(GaugeController, accounts, dfx, voting_escrow, master_account):
    yield GaugeController.deploy(dfx, voting_escrow, {'from': master_account, 'gas_price': gas_strategy})


'''
Gauges
'''


@pytest.fixture(scope='module')
def three_gauges(RewardsOnlyGauge, mock_lp_token, master_account):
    contracts = [
        RewardsOnlyGauge.deploy(master_account, mock_lp_token, {
                                'from': master_account, 'gas_price': gas_strategy})
        for _ in range(3)
    ]
    yield contracts
