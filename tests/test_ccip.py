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
from utils.helper import fund_multisigs, mint_dfx, fund_multisigs1
from utils.ve import deposit_to_ve, submit_ve_vote
from .constants import EMISSION_RATE, TOTAL_DFX_REWARDS


# handle setup logic required for each unit test
@pytest.fixture(scope="function", autouse=True)
def setup(
    DFX,
    gauge_controller,
    three_gauges,
    distributor,
    deploy_account,
    multisig_0,
    DFXTokenTransfer
):

    fund_multisigs(deploy_account, [multisig_0])
    # setup gauges and distributor
    #setup_gauge_controller(gauge_controller, three_gauges, multisig_0)

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
def test_ccip(
    gauge_controller,
    multisig_0,
    DFXTokenTransfer,
    deploy_account
):
    fund_multisigs1(deploy_account, DFXTokenTransfer)

    addy = gauge_controller.ccip_send(DFXTokenTransfer,  {"gas_price": 1190958123232})


    print("Msg Sent")
    print(gauge_controller.msgSent)
    print("Address")
    print(addy.return_value)
    print(DFXTokenTransfer)

    # gauge_controller.change_gauge_weight(
    #     gauge, 1 * 1e18, {"from": multisig_0, "gas_price": gas_strategy}
    # )


