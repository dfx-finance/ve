#!/usr/bin/env python
import brownie
from datetime import datetime, timedelta
import pytest

from utils.chain import fastforward_chain, gas_strategy
from utils.constants import EMISSION_RATE, WEEK
from utils.gauges import setup_distributor, setup_gauge_controller, TOTAL_DFX_REWARDS
from utils.testing.token import fund_multisig


# handle setup logic required for each unit test
@pytest.fixture(scope='module', autouse=True)
def setup(dfx, gauge_controller, three_liquidity_gauges_v4, distributor, master_account, new_master_account):
    fund_multisig(master_account)

    # setup gauges and distributor
    setup_gauge_controller(
        gauge_controller, three_liquidity_gauges_v4, master_account)

    # Params:
    # - reward token
    # - distributor contract
    # - account from which to mint and provide rewards to distributor contract
    # - account which administers the distributor contract
    # - rate dependent on tokens available and weekly reduction (see spreadsheet)
    setup_distributor(dfx, distributor, master_account,
                      new_master_account, EMISSION_RATE)


@pytest.fixture(scope='module', autouse=True)
def teardown():
    yield
    brownie.chain.reset()


def test_full_distribution(dfx, three_liquidity_gauges_v4, distributor, master_account):
    # init 10s before the week change
    t0 = brownie.chain.time()
    t1 = (t0 + 2 * WEEK) // WEEK * WEEK - 10
    brownie.chain.sleep(t1 - t0)

    # assert advancing 1 week after deployment plus some # of days until wednesday before new epoch
    assert 7 < timedelta(seconds=t1 - t0).days < 14
    # assert advance day is a wednesday
    assert datetime.fromtimestamp(t1).weekday() == 2

    total_distributed = 0
    for i in range(207):
        distributor.distributeRewardToMultipleGauges(
            three_liquidity_gauges_v4, {'from': master_account, 'gas_price': gas_strategy})

        distributor_balance = dfx.balanceOf(distributor)
        distributed_amount = (TOTAL_DFX_REWARDS -
                              distributor_balance) - total_distributed

        total_distributed += distributed_amount

        # epoch, startEpochSupply, calculatedDistributed, actuallyDistributed = expected[i]
        # assert distributor.miningEpoch() == epoch
        # assert distributor.startEpochSupply() == startEpochSupply
        # assert total_distributed == calculatedDistributed
        # assert (TOTAL_DFX_REWARDS - distributor_balance) == actuallyDistributed
        print('-----')
        print(f'Epoch: {distributor.miningEpoch()}')
        print(f'Start epoch supply: {distributor.startEpochSupply() / 1e18}')
        print(f'Tallied distributed: {total_distributed / 1e18}')
        print(f'Actually distributed: {(TOTAL_DFX_REWARDS - distributor_balance) / 1e18}')

        fastforward_chain(num_weeks=1, delta=10)
