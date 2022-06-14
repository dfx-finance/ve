from brownie import Contract
from brownie.network.gas.strategies import LinearScalingStrategy
import json
import pytest

import addresses

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('60 gwei', '150 gwei', 1.3)


# Load existing DFX ERC20 from mainnet fork
@pytest.fixture(scope='module')
def dfx():
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
