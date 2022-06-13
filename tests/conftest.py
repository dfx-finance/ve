from brownie import Contract
from brownie.network.gas.strategies import LinearScalingStrategy
import json
import pytest

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy("60 gwei", "150 gwei", 1.3)


# Load existing DFX ERC20 from mainnet fork
@pytest.fixture(scope="module")
def DFX():
    abi = json.load(open("./tests/abis/Dfx.json"))
    yield Contract.from_abi("DFX", "0x888888435FDe8e7d4c54cAb67f206e4199454c60", abi)


@pytest.fixture(scope="module")
def voting_escrow(VotingEscrow, accounts, DFX):
    yield VotingEscrow.deploy(
        DFX, "Voting-escrowed DFX", "veDFX", "veCRV_0.99", {
            "from": accounts[0], 'gas_price': gas_strategy}
    )


@pytest.fixture(scope="module")
def gauge_controller(GaugeController, accounts, DFX, voting_escrow):
    yield GaugeController.deploy(DFX, voting_escrow, {"from": accounts[0], 'gas_price': gas_strategy})
