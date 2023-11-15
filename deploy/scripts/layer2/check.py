#!/usr/bin/env python
from brownie import chain, Contract
from brownie import (
    clDFX,
    ChildChainReceiver,
    ChildChainStreamer,
    MigrationReceiver,
    Migrator,
    RewardsOnlyGauge,
)

from utils.ccip import ETHEREUM_CHAIN_SELECTOR
from utils.checker import Checker
from utils.config import INSTANCE_ID
from utils.logger import load_inputs, load_outputs
from utils.network import connected_network

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)

GAUGES = {
    137: [
        ["cadcUsdcReceiver", "cadcUsdcStreamer", "cadcUsdcGauge", "cadcUsdcLpt"],
        ["ngncUsdcReceiver", "ngncUsdcStreamer", "ngncUsdcGauge", "ngncUsdcLpt"],
        ["trybUsdcReceiver", "trybUsdcStreamer", "trybUsdcGauge", "trybUsdcLpt"],
        ["xsgdUsdcReceiver", "xsgdUsdcStreamer", "xsgdUsdcGauge", "xsgdUsdcLpt"],
        ["usdceUsdcReceiver", "usdceUsdcStreamer", "usdceUsdcGauge", "usdceUsdcLpt"],
    ],
    42161: [
        ["cadcUsdcReceiver", "cadcUsdcStreamer", "cadcUsdcGauge", "cadcUsdcLpt"],
        ["gyenUsdcReceiver", "gyenUsdcStreamer", "gyenUsdcGauge", "gyenUsdcLpt"],
        ["usdceUsdcReceiver", "usdceUsdcStreamer", "usdceUsdcGauge", "usdceUsdcLpt"],
    ],
}


def main():
    """
    CCIP DFX
    """
    dfx = clDFX.at(existing.read_addr("DFX"))
    Checker._value(dfx.name(), "DFX Token (L2)", "DFX token name")
    Checker._value(dfx.symbol(), "DFX", "DFX token symbol")

    # ChildChainReceiver, ChildChainStreamer, RewardsOnlyGauge
    for gauge_key_set in GAUGES[chain.id]:
        receiver_key, streamer_key, gauge_key, lpt_key = gauge_key_set

        """
        ChildChainReceiver
        """
        print(
            "-- Checking ChildChainReceiver ({key}): {addr}".format(
                key=receiver_key, addr=deployed.read_addr(receiver_key)
            )
        )

        receiver = ChildChainReceiver.at(deployed.read_addr(receiver_key))
        # owner
        Checker.address(
            receiver.owner(),
            existing.read_addr("multisig0"),
            "ChildChainReceiver admin",
            # debug_addr=existing.read_addr("deployer1"),
        )
        Checker._value(
            receiver.whitelistedSourceChains(ETHEREUM_CHAIN_SELECTOR),
            True,
            "ChildChainReceiver whitelisted source chain",
        )
        Checker._value(
            receiver.whitelistedSenders(existing.read_addr("ccipSenderEth")),
            True,
            "ChildChainReceiver whitelisted sender",
        )
        Checker.address(
            receiver.streamer(),
            deployed.read_addr(streamer_key),
            "ChildChainReceiver streamer",
        )
        Checker.number_gt(receiver.balance(), 0, "ChildChainReceiver gas money")

        """
        ChildChainStreamer
        """
        print(
            "-- Checking ChildChainStreamer ({key}): {addr}".format(
                key=streamer_key, addr=deployed.read_addr(streamer_key)
            )
        )

        streamer = ChildChainStreamer.at(deployed.read_addr(streamer_key))
        # owner
        Checker.address(
            streamer.owner(),
            existing.read_addr("multisig0"),
            "ChildChainStreamer admin",
            # debug_addr=existing.read_addr("deployer1"),
        )
        Checker.address(
            streamer.reward_receiver(),
            deployed.read_addr(gauge_key),
            "ChildChainStreamer receiver (gauge)",
        )
        Checker.address(
            streamer.reward_tokens(0),
            existing.read_addr("DFX"),
            "ChildChainStreamer 0th reward (DFX)",
        )
        Checker.number(streamer.reward_count(), 1, "ChildChainStreamer num rewards")
        Checker.address(
            streamer.reward_data(existing.read_addr("DFX"))[0],
            deployed.read_addr(receiver_key),
            "ChildChainStreamer DFX receiver",
        )

        """
        RewardsOnlyGauge
        """
        print(
            "-- Checking RewardsOnlyGauge ({key}): {addr}".format(
                key=gauge_key, addr=deployed.read_addr(gauge_key)
            )
        )

        gauge = Contract.from_abi(
            "RewardsOnlyGauge", deployed.read_addr(gauge_key), RewardsOnlyGauge.abi
        )
        # owner
        Checker.address(
            gauge.admin(),
            existing.read_addr("multisig0"),
            "RewardOnlyGauge admin",
            # debug_addr=existing.read_addr("deployer1"),
        )
        Checker.address(
            gauge.lp_token(), existing.read_addr(lpt_key), "RewardOnlyGauge lpt"
        )
        Checker.address(
            gauge.reward_tokens(0),
            existing.read_addr("DFX"),
            "RewardOnlyGauge DFX reward",
        )

    """
    Migrator
    """
    print("-- Checking Migrator: {addr}".format(addr=deployed.read_addr("migrator")))

    migrator = Migrator.at(deployed.read_addr("migrator"))
    # owner
    Checker.address(migrator.owner(), existing.read_addr("multisig0"), "Migrator admin")
    Checker.address(
        migrator.bridgedDfx(),
        existing.read_addr("bridgedDFX"),
        "Migrator DFX (bridged)",
    )
    Checker.address(
        migrator.ccipDfx(), existing.read_addr("DFX"), "Migrator DFX (CCIP)"
    )

    """
    MigrationReceiver
    """
    print(
        "-- Checking MigrationReceiver: {addr}".format(
            addr=deployed.read_addr("migrationReceiver")
        )
    )
    receiver = MigrationReceiver.at(deployed.read_addr("migrationReceiver"))
    # owner
    Checker.address(
        receiver.owner(), existing.read_addr("multisig0"), "MigrationReceiver admin"
    )
    Checker.number(
        receiver.whitelistedSourceChain(),
        existing.read_addr("chainSelectorEth"),
        "MigrationReceiver source chain selector",
    )
    Checker.address(
        receiver.whitelistedSender(),
        existing.read_addr("ccipSenderEth"),
        "MigrationReceiver source sender",
    )
    Checker.address(
        receiver.migrator(),
        deployed.read_addr("migrator"),
        "MigrationReceiver migrator",
    )


if __name__ == "__main__":
    main()
