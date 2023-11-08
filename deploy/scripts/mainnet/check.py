#!/usr/bin/env python
from brownie import web3, ZERO_ADDRESS
from brownie import (
    VeDFX,
    VeBoostProxy,
    GaugeController,
    DfxDistributor,
    CcipSender,
    LiquidityGaugeV4,
    CcipRootGauge,
)


from utils.checker import Checker
from utils.config import INSTANCE_ID
from utils.logger import load_inputs, load_outputs

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)

ARBITRUM_CHAIN_SELECTOR = 4949039107694359620
POLYGON_CHAIN_SELECTOR = 4051577828743386545
GAUGES = [
    # mainnet
    ["ethereum", "ethereumCadcUsdcGauge", None, None],
    ["ethereum", "ethereumGbptUsdcGauge", None, None],
    ["ethereum", "ethereumGyenUsdcGauge", None, None],
    ["ethereum", "ethereumTrybUsdcGauge", None, None],
    ["ethereum", "ethereumXidrUsdcGauge", None, None],
    ["ethereum", "ethereumXsgdUsdcGauge", None, None],
    # arbitrum
    ["arbitrum", "arbitrumCadcUsdcRootGauge", ARBITRUM_CHAIN_SELECTOR, None],
    ["arbitrum", "arbitrumGyenUsdcRootGauge", ARBITRUM_CHAIN_SELECTOR, None],
    # polygon
    ["polygon", "polygonCadcUsdcRootGauge", POLYGON_CHAIN_SELECTOR, None],
    ["polygon", "polygonNgncUsdcRootGauge", POLYGON_CHAIN_SELECTOR, None],
    ["polygon", "polygonTrybUsdcRootGauge", POLYGON_CHAIN_SELECTOR, None],
    ["polygon", "polygonXsgdUsdcRootGauge", POLYGON_CHAIN_SELECTOR, None],
]
CCIP_GAUGE_MAP = {
    row[1]: {"selector": row[2], "receiver": row[3]} for row in GAUGES if row[2]
}
ETHEREUM_GAUGE_KEYS = [row[1] for row in filter(lambda g: g[0] == "ethereum", GAUGES)]
L2_GAUGE_KEYS = [row[1] for row in filter(lambda g: g[0] != "ethereum", GAUGES)]


def main():
    """
    veDFX
    """
    veDFX = VeDFX.at(existing.read_addr("veDFX"))
    # owner
    Checker.address(
        veDFX.admin(),
        existing.read_addr("multisig0"),
        "veDFX admin",
        debug_addr="0x945D3D5CA590701C2C357309648Adcd70d4D8E9b",
    )
    # collateral (DFX)
    Checker.address(veDFX.token(), existing.read_addr("DFX"), "veDFX collateral (DFX)")

    """
    veBoostProxy
    """
    veBoostProxy = VeBoostProxy.at(deployed.read_addr("veBoostProxy"))
    # owner
    Checker.address(
        veBoostProxy.admin(), existing.read_addr("multisig0"), "veBoostProxy admin"
    )
    Checker.address(
        veBoostProxy.voting_escrow(),
        existing.read_addr("veDFX"),
        "veBoostProxy veDFX",
    )
    Checker.address(veBoostProxy.delegation(), ZERO_ADDRESS, "veBoostProxy delegation")

    """
    Gauge Controller
    """
    gaugeController = GaugeController.at(deployed.read_addr("gaugeController"))
    # owner
    Checker.address(
        gaugeController.admin(),
        existing.read_addr("multisig0"),
        "GaugeController admin",
        debug_addr=existing.read_addr("deployer0"),
    )
    Checker.address(
        gaugeController.token(),
        existing.read_addr("DFX"),
        "GaugeController rewards token (DFX)",
    )
    Checker.address(
        gaugeController.voting_escrow(),
        existing.read_addr("veDFX"),
        "GaugeController voting token (veDFX)",
    )
    print("SKIP - GaugeController gauges not registered (Nov 6, 2023)")
    # Checker.number(gaugeController.n_gauges(), 10, "GaugeController num gauges")
    # for key in [*ETHEREUM_GAUGE_KEYS, *L2_GAUGE_KEYS]:
    #     if gaugeController.gauge_types(deployed.read_addr(key)) == 0:
    #         print(
    #             Fore.GREEN
    #             + f"PASS - GaugeController: {key} is registered"
    #             + Style.RESET_ALL
    #         )
    #     else:
    #         print(
    #             Fore.RED
    #             + f"FAIL - GaugeController: {key} is not registered"
    #             + Style.RESET_ALL
    #         )

    """
    DfxDistributor
    """
    print("SKIP - DfxDistributor not available")
    # dfx_distributor = DfxDistributor.at(deployed.read_addr("dfxDistributor"))
    # # owner
    # Checker.address(
    #     dfx_distributor.admin(),
    #     existing.read_addr("multisig0"),
    #     "DfxDistributor admin",
    #     debug_addr=existing.read_addr("deployer1"),
    # )
    # Checker.address(
    #     dfx_distributor.controller(),
    #     existing.read_addr("gaugeController"),
    #     "DfxDistributor gauge controller",
    # )
    # Checker.address(
    #     dfx_distributor.reward_token(),
    #     existing.read_addr("DFX"),
    #     "DfxDistributor reward token (DFX)",
    # )
    # # roles
    # default_admin_role = dfx_distributor.DEFAULT_ADMIN_ROLE()
    # governor_role = dfx_distributor.GOVERNOR_ROLE()
    # guardian_role = dfx_distributor.GUARDIAN_ROLE()
    # Checker.address(
    #     dfx_distributor.getRoleAdmin(default_admin_role),
    #     ZERO_ADDRESS,  # Default admin should not be set
    #     "DfxDistributor default admin",
    # )
    # Checker.address(
    #     dfx_distributor.getRoleAdmin(governor_role),
    #     governor_role,  # Governor should be own admin
    #     "DfxDistributor governor admin",
    # )
    # Checker.address(
    #     dfx_distributor.getRoleAdmin(guardian_role),
    #     governor_role,  # Governor should be guardian admin
    #     "DfxDistributor guardian admin",
    # )
    # Checker.has_role(
    #     dfx_distributor,
    #     default_admin_role,
    #     existing.read_addr("multsig0"),
    #     "DfxDistributor multsig admin",
    #     reverse=True,
    # )
    # Checker.has_role(
    #     dfx_distributor,
    #     governor_role,
    #     existing.read_addr("multsig0"),
    #     "DfxDistributor mulitsig governor",
    # )
    # Checker.has_role(
    #     dfx_distributor,
    #     guardian_role,
    #     existing.read_addr("multsig0"),
    #     "DfxDistributor mulitsig guardian",
    # )

    """
    CcipSender
    """
    ccipSender = CcipSender.at(deployed.read_addr("ccipSender"))
    # owner
    Checker.address(
        ccipSender.admin(),
        existing.read_addr("multisig0"),
        "CCIPSender admin",
        debug_addr=existing.read_addr("deployer1"),
    )
    Checker.address(
        ccipSender.DFX(), existing.read_addr("DFX"), "CCIPSender token (DFX)"
    )
    Checker.address(
        ccipSender.router(), existing.read_addr("ccipRouter"), "CCIPSender router"
    )
    for key, ccip_info in CCIP_GAUGE_MAP.items():
        receiver, chain_selector = ccipSender.destinations(deployed.read_addr(key))
        if receiver == ZERO_ADDRESS:
            print("SKIP - CCIPSender gauges not registered (Nov 6, 2023)")
        else:
            Checker.number(
                chain_selector,
                ccip_info["selector"],
                f"CCIPSender {key} chain selector",
            )
            Checker.address(
                receiver, ccip_info["receiver"], f"CCIPSender {key} receiver"
            )

    arb_fee_token, arb_fee_amount = ccipSender.chainFees(ARBITRUM_CHAIN_SELECTOR)
    Checker.address(arb_fee_token, ZERO_ADDRESS, "CCIPSender fee token (Arbitrum)")
    Checker.number(arb_fee_amount, 200_00, "CCIPSender fee amount (Arbitrum)")
    pol_fee_token, pol_fee_amount = ccipSender.chainFees(ARBITRUM_CHAIN_SELECTOR)
    Checker.address(pol_fee_token, ZERO_ADDRESS, "CCIPSender fee token (Polygon)")
    Checker.number(pol_fee_amount, 200_00, "CCIPSender fee amount (Polygon)")

    """
    LiquidityGaugeV4
    """
    ## DEV: eth gauges not yet deployed (Nov 6, 2023)
    # for key in ETHEREUM_GAUGE_KEYS:
    #     gauge = LiquidityGaugeV4.at(deployed.read_addr(key))
    #     # owner
    #     Checker.address(
    #         gauge.admin(),
    #         existing.read_addr("multisig0"),
    #         f"{key} admin",
    #         debug_addr=existing.read_addr("deployer1"),
    #     )
    #     Checker.address(gauge.DFX(), existing.read_addr("DFX"), f"{key} DFX")
    #     Checker.address(
    #         gauge.distributor(),
    #         deployed.read_addr("dfxDistributor"),
    #         f"{key} distributor",
    #         debug_addr=existing.read_addr("deployer1"),
    #     )
    #     Checker.address(
    #         gauge.veBoost_proxy(),
    #         deployed.read_addr("veBoostProxy"),
    #         f"{key} veBoostProxy",
    #     )

    """
    RootChainGauges
    """

    def _check_root_chain_gauge(json_key):
        gauge = CcipRootGauge.at(deployed.read_addr(json_key))
        # owner
        Checker.address(
            gauge.admin(),
            existing.read_addr("multisig0"),
            f"{json_key} admin",
            debug_addr=existing.read_addr("deployer1"),
        )
        Checker.address(gauge.DFX(), existing.read_addr("DFX"), f"{json_key} DFX")
        Checker.address(
            gauge.distributor(),
            deployed.read_addr("dfxDistributor"),
            f"{json_key} distributor",
            debug_addr=existing.read_addr("deployer1"),
        )
        ## DEV: method not public
        # Checker.address(
        #     gauge.sender(),
        #     deployed.read_addr("dfxDistributor"),
        #     f"{json_key} distributor",
        #     debug_addr=existing.read_addr("deployer1"),
        # )

    for key in L2_GAUGE_KEYS:
        _check_root_chain_gauge(key)


if __name__ == "__main__":
    main()
