#!/usr/bin/env python
import brownie
from datetime import datetime, timedelta
import pytest

from fork.constants import EMISSION_RATE, WEEK
from utils.chain import fastforward_chain_weeks
from utils.gauges import setup_distributor, setup_gauge_controller, TOTAL_DFX_REWARDS
from utils.gas import gas_strategy
from utils.helper import fund_multisigs


# handle setup logic required for each unit test
@pytest.fixture(scope="module", autouse=True)
def setup(
    dfx,
    gauge_controller,
    three_liquidity_gauges_v4,
    distributor,
    master_account,
    new_master_account,
):
    fund_multisigs(master_account)

    # setup gauges and distributor
    setup_gauge_controller(gauge_controller, three_liquidity_gauges_v4, master_account)

    # Params:
    # - reward token
    # - distributor contract
    # - account from which to mint and provide rewards to distributor contract
    # - account which administers the distributor contract
    # - rate dependent on tokens available and weekly reduction (see spreadsheet)
    setup_distributor(
        dfx, distributor, master_account, new_master_account, EMISSION_RATE
    )


@pytest.fixture(scope="module", autouse=True)
def teardown():
    yield
    brownie.chain.reset()


def test_full_distribution(dfx, three_liquidity_gauges_v4, distributor, master_account):
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
        (
            1,
            120206956897440000000000,
            1.192732992438352e23,
            1.192732992438352e23,
        ),  # epoch 1
        (2, 239480256141274416710400, 2.3762019263243358e23, 2.3762019263243358e23),
        (3, 357827149529873622547200, 3.550478756388339e23, 3.550478756388339e23),
        (4, 475254832536273536409600, 4.715634878482198e23, 4.715634878482198e23),
        (5, 591770444745659284627200, 5.871741133920114e23, 5.871741133920114e23),
    ]

    # init 10s before the week change
    t0 = brownie.chain.time()
    t1 = (t0 + 2 * WEEK) // WEEK * WEEK - 10
    brownie.chain.sleep(t1 - t0)

    # assert advancing 1 week after deployment plus some # of days until wednesday before new epoch
    assert 7 < timedelta(seconds=t1 - t0).days < 14
    # assert advance day is a wednesday
    assert datetime.fromtimestamp(t1).weekday() == 2

    total_distributed = 0
    for i in range(5):
        distributor.distributeRewardToMultipleGauges(
            three_liquidity_gauges_v4,
            {"from": master_account, "gas_price": gas_strategy},
        )

        distributor_balance = dfx.balanceOf(distributor)
        distributed_amount = (
            TOTAL_DFX_REWARDS - distributor_balance
        ) - total_distributed

        total_distributed += distributed_amount

        epoch, startEpochSupply, calculatedDistributed, actuallyDistributed = expected[
            i
        ]
        assert distributor.miningEpoch() == epoch
        assert distributor.startEpochSupply() == startEpochSupply
        assert total_distributed == calculatedDistributed
        assert (TOTAL_DFX_REWARDS - distributor_balance) == actuallyDistributed

        fastforward_chain_weeks(num_weeks=1, delta=10)
