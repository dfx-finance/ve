# References:
# 1. https://github.com/curvefi/curve-dao-contracts/blob/master/tests/integration/GaugeController/test_vote_weight.py
from brownie import chain
from brownie.network.gas.strategies import LinearScalingStrategy

WEEK = 86400 * 7
YEAR = 86400 * 365

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy("60 gwei", "150 gwei", 1.3)


def test_gauge_weight_vote(gauge_controller, voting_escrow):
    """
    Test that gauge weights correctly adjust over time.
    """
    t0 = chain.time()
    t1 = (t0 + 2 * WEEK) // WEEK * WEEK - 10

    # Deposit for voting
    voting_escrow.create_lock(1e18, t1, {"gas_price": gas_strategy})
