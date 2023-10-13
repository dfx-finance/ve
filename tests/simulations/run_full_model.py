#!/usr/bin/env python
import brownie
from datetime import datetime, timedelta
import pytest

from tests.simulations.constants import EMISSION_RATE, TOTAL_DFX_REWARDS
from utils.chain import fastforward_chain_weeks
from utils.gauges import setup_distributor, setup_gauge_controller
from utils.gas import gas_strategy
from utils.helper import fund_multisigs
from utils.constants import WEEK


# handle setup logic required for each unit test
@pytest.fixture(scope="function", autouse=True)
def setup(
    DFX, gauge_controller, three_gauges_L1, distributor, deploy_account, multisig_0
):
    fund_multisigs(deploy_account, [multisig_0])

    # setup gauges and distributor
    setup_gauge_controller(gauge_controller, three_gauges_L1, multisig_0)

    # Params:
    # - reward token
    # - distributor contract
    # - account from which to mint and provide rewards to distributor contract
    # - account which administers the distributor contract
    # - rate dependent on tokens available and weekly reduction (see spreadsheet)
    setup_distributor(
        DFX, distributor, deploy_account, multisig_0, EMISSION_RATE, TOTAL_DFX_REWARDS
    )


@pytest.fixture(scope="function", autouse=True)
def teardown():
    yield
    brownie.chain.reset()


def test_full_distribution(DFX, three_gauges_L1, distributor, multisig_0):
    # init 10s before the week change
    t0 = brownie.chain.time()
    t1 = (t0 + 2 * WEEK) // WEEK * WEEK - 10
    brownie.chain.sleep(t1 - t0)
    print(t1 - t0)
    return

    # assert advancing 1 week after deployment plus some # of days until wednesday before new epoch
    assert 7 < timedelta(seconds=t1 - t0).days < 14
    # assert advance day is a wednesday
    assert datetime.fromtimestamp(t1).weekday() == 2

    total_distributed = 0
    for i in range(52):
        distributor.distributeRewardToMultipleGauges(
            three_gauges_L1,
            {"from": multisig_0, "gas_price": gas_strategy},
        )

        distributor_balance = DFX.balanceOf(distributor)
        distributed_amount = (
            TOTAL_DFX_REWARDS - distributor_balance
        ) - total_distributed

        total_distributed += distributed_amount

        # epoch, startEpochSupply, calculatedDistributed, actuallyDistributed = expected[i]
        # assert distributor.miningEpoch() == epoch
        # assert distributor.startEpochSupply() == startEpochSupply
        # assert total_distributed == calculatedDistributed
        # assert (TOTAL_DFX_REWARDS - distributor_balance) == actuallyDistributed
        print("-----")
        print(f"Epoch: {distributor.miningEpoch()}")
        print(f"Start epoch supply: {distributor.startEpochSupply() / 1e18}")
        print(f"Tallied distributed: {total_distributed / 1e18}")
        print(
            f"Actually distributed: {(TOTAL_DFX_REWARDS - distributor_balance) / 1e18}"
        )

        fastforward_chain_weeks(num_weeks=1, delta=0)
