#!/usr/bin/env python
from brownie import chain
import math
import pytest

from utils.apr import mint_lp_tokens
from utils.chain import (
    fastforward_chain,
    fastforward_chain_weeks,
    # fastforward_chain_anvil as fastforward_chain,
    # fastforward_chain_weeks_anvil as fastforward_chain_weeks,
)
from utils.gauges import deposit_lp_tokens, setup_distributor, setup_gauge_controller
from utils.gas import gas_strategy
from utils.helper import fund_multisigs, mint_dfx
from utils.ve import deposit_to_ve, submit_ve_vote
from .constants import EMISSION_RATE, TOTAL_DFX_REWARDS


# handle setup logic required for each unit test
@pytest.fixture(scope="function", autouse=True)
def setup(
    DFX,
    root_gauge_L1,
    distributor,
    deploy_account,
    multisig_0,
):
    fund_multisigs(deploy_account, [multisig_0])

    # setup gauges and distributor
    # setup_gauge_controller(gauge_controller, three_gauges, multisig_0)

    # Params:
    # - reward token
    # - distributor contract
    # - account from which to mint and provide rewards to distributor contract
    # - account which administers the distributor contract
    # - rate dependent on tokens available and weekly reduction (see spreadsheet)
    setup_distributor(
        DFX,
        distributor,
        deploy_account,
        multisig_0,
        EMISSION_RATE,
        TOTAL_DFX_REWARDS,
    )


@pytest.fixture(scope="function", autouse=True)
def teardown():
    yield
    chain.reset()


##
## Tests
##


def test_RootGauge(
    root_gauge_L1, distributor, mock_ccip_router, deploy_account, multisig_0
):
    print("Msg Sent", root_gauge_L1, distributor)

    root_gauge_L1.update_distributor(
        deploy_account, {"from": multisig_0, "gas_price": gas_strategy}
    )

    print("Msg Sent", root_gauge_L1)

    tx = root_gauge_L1.notifyRewardTest(
        mock_ccip_router, 1, {"from": deploy_account, "gas_price": gas_strategy}
    )

    print(tx.info())
    print(tx)
    print(tx.return_value)
