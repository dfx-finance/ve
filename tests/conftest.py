from os import access
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
    yield VotingEscrow.deploy(
        dfx, 'Voting-escrowed DFX', 'veDFX', 'veCRV_0.99', {
            'from': accounts[0], 'gas_price': gas_strategy}
    )


@pytest.fixture(scope='module')
def gauge_controller(GaugeController, accounts, dfx, voting_escrow):
    yield GaugeController.deploy(dfx, voting_escrow, {'from': accounts[0], 'gas_price': gas_strategy})
