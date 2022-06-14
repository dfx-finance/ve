# References:
# 1. https://github.com/curvefi/curve-dao-contracts/blob/master/tests/integration/GaugeController/test_vote_weight.py
from brownie import chain
from brownie.network.gas.strategies import LinearScalingStrategy
import pytest

import addresses

WEEK = 86400 * 7
YEAR = 86400 * 365

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('40 gwei', '150 gwei', 1.3)


# handle setup logic required for each unit test
@pytest.fixture(scope='module', autouse=True)
def setup(dfx, gauge_controller, voting_escrow, master_account, user_accounts):
    master_account.transfer(addresses.DFX_OWNER, '10 ether',
                            gas_price=gas_strategy)
    dfx.mint(master_account, 10 * 10e18,
             {'from': addresses.DFX_OWNER, 'gas_price': gas_strategy})

    for acct in user_accounts:
        dfx.transfer(acct, 1 * 10e18,
                     {'from': master_account, 'gas_price': gas_strategy})
        dfx.approve(voting_escrow, 10e24,
                    {'from': acct, 'gas_price': gas_strategy})


def test_gauge_weight_vote(dfx, gauge_controller, voting_escrow, user_accounts):
    '''
    Test that gauge weights correctly adjust over time.
    '''
    t0 = chain.time()
    t1 = (t0 + 2 * WEEK) // WEEK * WEEK - 10

    # Deposit for voting
    voting_escrow.create_lock(
        1 * 1e18, t1, {'from': user_accounts[0], 'gas_price': gas_strategy})


def test_transfer_ownership(gauge_controller):
    # new_admin_addr = 0x0000000000000000000000000
    # gauge_controller.commit_transfer_ownership(
    #     new_admin_addr, {'gas_price': gas_strategy})
    # gauge_controller.apply_transfer_ownership(
    #     new_admin_addr, {'gas_price': gas_strategy})
    pass
