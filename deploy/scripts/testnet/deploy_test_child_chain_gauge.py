#!/usr/bin/env python
from brownie import Contract, ZERO_ADDRESS
from brownie import (
    ERC20LP,
    RewardsOnlyGauge,
    DfxUpgradeableProxy,
    ChildChainStreamer,
    ChildChainReceiver,
)
import time

from utils.config import (
    DEPLOY_ACCT,
    DEPLOY_PROXY_ACCT,
    VERIFY_CONTRACTS,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.network import connected_network, is_localhost


# deploy l2 rewards-only gauge
def deploy_gauge_implementation() -> RewardsOnlyGauge:
    print(f"--- Deploying L2 gauge implementation contract to {connected_network} ---")
    gauge_logic = RewardsOnlyGauge.deploy({"from": DEPLOY_ACCT})
    if not is_localhost:
        time.sleep(3)  # wait to prevent "contract not available"
    return gauge_logic


# deploy gauge proxy and initialize
def deploy_gauge(gauge_logic: RewardsOnlyGauge, lpt: ERC20LP) -> RewardsOnlyGauge:
    print(f"--- Deploying L2 gauge proxy contract to {connected_network} ---")
    gauge_initializer_calldata = gauge_logic.initialize.encode_input(DEPLOY_ACCT, lpt)
    proxy = DfxUpgradeableProxy.deploy(
        gauge_logic.address,
        DEPLOY_PROXY_ACCT,
        gauge_initializer_calldata,
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )
    gauge = Contract.from_abi("RewardsOnlyGauge", proxy, RewardsOnlyGauge.abi)
    return gauge


# deploy childchainstreamer
def deploy_streamer(
    gauge: RewardsOnlyGauge, rewards_token: ERC20LP
) -> ChildChainStreamer:
    print(f"--- Deploying ChildChainStreamer contract to {connected_network} ---")
    streamer = ChildChainStreamer.deploy(
        DEPLOY_ACCT,
        gauge,
        rewards_token,
        {"from": DEPLOY_ACCT},
    )
    return streamer


# deploy childchainreceiver
def deploy_receiver(
    streamer: ChildChainStreamer, ccip_router: str
) -> ChildChainReceiver:
    print(f"--- Deploying Receiver contract to {connected_network} ---")
    receiver = ChildChainReceiver.deploy(
        ccip_router,
        streamer,
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )
    return receiver


def configure(
    receiver: ChildChainReceiver,
    streamer: ChildChainStreamer,
    gauge: RewardsOnlyGauge,
    rewards_token: ERC20LP,
):
    print(
        f"--- Configuring ChildChainStreamer contract with ChildChainReceiver as reward distributor ---"
    )

    # update authorized user for childchainstreamer rewards
    # DEV: This will be the address of the CCTP contract which is calling "notify_reward_amount"
    # on ChildChainStreamer
    streamer.set_reward_distributor(
        rewards_token, receiver.address, {"from": DEPLOY_ACCT}
    )

    print(f"--- Configuring RewardsOnlyGauge contract with DFX rewards ---")
    # set rewards contract on gauge
    # DEV: cannot be set while gauge has 0 deposits?
    gauge.set_rewards(
        streamer,
        streamer.signatures["get_reward"],
        [
            rewards_token,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
        ],
        {"from": DEPLOY_ACCT},
    )


def main():
    rewards_token = ERC20LP.at("0x48Ef554e293392089A1E7b50631e10fBFbB57456")
    lpt = ERC20LP.at("0x90e19C5ef79Ad9BFb6E865A5214bFf432B27584c")
    ccip_router = DEPLOY_ACCT

    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    # gauge_logic = deploy_gauge_implementation()
    # gauge = deploy_gauge(gauge_logic, lpt)
    # streamer = deploy_streamer(gauge, rewards_token)
    # deploy_receiver(streamer, ccip_router)

    receiver = ChildChainReceiver.at("0xdd4388A4e76Cd8330004781363A1C2d5631b77B4")
    streamer = ChildChainStreamer.at("0x1fc5e93ad39f5D483889b3092d088f649155E7f8")
    gauge = RewardsOnlyGauge.at("0xBa38E95a19B02C1B581d4C3c3df5F22091c5c726")

    configure(receiver, streamer, gauge, rewards_token)


if __name__ == "__main___":
    main()
