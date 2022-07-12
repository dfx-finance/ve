from brownie import ZERO_ADDRESS, chain
from brownie.network.gas.strategies import LinearScalingStrategy
import pytest

import addresses

WEEK = 86400 * 7
DEFAULT_GAUGE_TYPE = 0  # Ethereum stableswap pools

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('30 gwei', '250 gwei', 1.3)


# handle setup logic required for each unit test
@pytest.fixture(scope='module', autouse=True)
def setup(dfx, gauge_controller, voting_escrow, three_liquidity_gauges_v4, master_account, user_accounts):
    # Setup gauges
    gauge_controller.add_type(
        'Liquidity', 1e18, {'from': master_account, 'gas_price': gas_strategy})
    for gauge in three_liquidity_gauges_v4:
        gauge_controller.add_gauge(
            gauge, DEFAULT_GAUGE_TYPE, {'from': master_account, 'gas_price': gas_strategy})


def test_claim_rewards(gauge_controller, three_liquidity_gauges_v4, user_accounts):
    raise Exception("WIP")

    for acct in user_accounts:
        for gauge in three_liquidity_gauges_v4:
            print(acct, dir(gauge))
            # print(gauge.reward_contract())
            print(gauge_controller.points_weight())
            break
        break
