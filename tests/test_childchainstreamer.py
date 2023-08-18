#!/usr/bin/env python
from brownie import chain, Contract, ZERO_ADDRESS
import pytest

from utils.chain import (
    fastforward_chain,
    fastforward_chain_weeks,
    # fastforward_chain_anvil as fastforward_chain,
    # fastforward_chain_weeks_anvil as fastforward_chain_weeks,
)
from utils.constants import (
    # DEFAULT_TYPE_WEIGHT,
    # DEFAULT_GAUGE_TYPE,
    DEFAULT_GAUGE_WEIGHT,
)
from utils.gauges import setup_distributor, setup_gauge_controller
from utils.gas import gas_strategy
from utils.helper import fund_multisigs
from .constants import EMISSION_RATE, TOTAL_DFX_REWARDS, WEEK


# handle setup logic required for each unit test
@pytest.fixture(scope="function", autouse=True)
def setup(
    DFX,
    gauge_controller,
    three_gauges,
    distributor,
    deploy_account,
    multisig_0,
):
    fund_multisigs(deploy_account, [multisig_0])


def test_stream_to_gauge(
    DFX_OFT, ERC20LP, ChildChainStreamer, RewardsOnlyGauge, deploy_account, multisig_0
):
    # deploy L2 LPT for depositing into gauge
    lpt = ERC20LP.deploy(
        "L2 Test Gauge",
        "L2TG",
        18,
        1e9,
        {"from": deploy_account, "gas_price": gas_strategy},
    )

    # deploy L2 read-only gauge
    # DEV: this gauge will distribute rewards pro-rata to staked LPTs by their share
    # in the gauge at the time rewards are received
    gauge = RewardsOnlyGauge.deploy(
        multisig_0, lpt, {"from": deploy_account, "gas_price": gas_strategy}
    )

    # deploy L2 reward distributor
    # DEV: This is a 1-to-1 relationship with the RewardsOnlyGauge
    streamer = ChildChainStreamer.deploy(
        multisig_0,
        gauge,
        DFX_OFT,
        {"from": deploy_account, "gas_price": gas_strategy},
    )

    distributor = deploy_account  # This will be the address of the CCTP contract which is calling ChildChainStreamer
