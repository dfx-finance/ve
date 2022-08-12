#!/usr/bin/env python
from brownie import chain
from datetime import datetime, timedelta
import pytest

from utils import fastforward_chain, fund_multisig, gas_strategy
from utils_gauges import setup_distributor, setup_gauge_controller, TOTAL_DFX_REWARDS
from utils_ve import EMISSION_RATE, WEEK


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


def test_full_distribution(dfx, mock_lp_tokens, three_liquidity_gauges_v4, distributor, master_account):
    # expected rewards amounts starting with epoch 1 (nothing distributed during epoch 0)
    # - epoch: miningEpoch according to the distributor contract
    # - startEpochSupply (Wei): the amount the contract has internally accounted for supplying.
    #       This begins counting immediately at the beginning of epoch 0 using the initial rate.
    #       This means the distributor accounts for 1 week of distribution using an unadjusted rate
    #       before rewards are actually sent to any gauge, beginning during epoch 1 (which will be adjusted by 1 week)
    # - calculatedDistrubted (int): the amount this test script has distributed according to its own value tracking
    # - actuallyDistributed (int): the true amount distributed by comparing the distributor's balance to the total rewards provided
    # [(epoch, startEpochSupply, calculatedDistributed, actuallyDistributed)]
    expected = [
        (1, 9697668953184354240000, 9.62234633397832e21,
            9.62234633397832e21),  # epoch 1
        (2, 19320015287162908886400,
            1.9169955085938145e22, 1.9169955085938145e22),
        (3, 28867624039122580656000,
            2.8643406749032155e22, 2.8643406749032155e22),
        (4, 38341075702216718793600,
            3.804327730767447e22, 3.804327730767447e22),
        (5, 47740946260858999545600,
            4.737013827255874e22, 4.737013827255874e22),
    ]

    # init 10s before the week change
    t0 = chain.time()
    t1 = (t0 + 2 * WEEK) // WEEK * WEEK - 10
    chain.sleep(t1 - t0)

    # assert advancing 1 week after deployment plus some # of days until wednesday before new epoch
    assert 7 < timedelta(seconds=t1 - t0).days < 14
    # assert advance day is a wednesday
    assert datetime.fromtimestamp(t1).weekday() == 2

    total_distributed = 0
    for i in range(5):
        distributor.distributeRewardToMultipleGauges(
            three_liquidity_gauges_v4, {'from': master_account, 'gas_price': gas_strategy})

        distributor_balance = dfx.balanceOf(distributor)
        distributed_amount = (TOTAL_DFX_REWARDS -
                              distributor_balance) - total_distributed

        total_distributed += distributed_amount

        epoch, startEpochSupply, calculatedDistributed, actuallyDistributed = expected[i]
        assert distributor.miningEpoch() == epoch
        assert distributor.startEpochSupply() == startEpochSupply
        assert total_distributed == calculatedDistributed
        assert (TOTAL_DFX_REWARDS - distributor_balance) == actuallyDistributed

        fastforward_chain(WEEK)
