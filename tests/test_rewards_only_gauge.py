from brownie.network.gas.strategies import LinearScalingStrategy
import pytest

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('80 gwei', '250 gwei', 1.3)


# handle setup logic required for each unit test
@pytest.fixture(scope='module', autouse=True)
def setup(gauge_controller, three_gauges, master_account):
    # Setup gauges
    default_gauge_weight = 0

    gauge_controller.add_type(
        'Liquidity', 1e18, {'from': master_account, 'gas_price': gas_strategy})
    for gauge in three_gauges:
        gauge_controller.add_gauge(
            gauge, default_gauge_weight, {'from': master_account, 'gas_price': gas_strategy})


def test_claim_rewards():
    pass
