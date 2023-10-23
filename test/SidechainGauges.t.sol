// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";

import "./utils/Constants.sol";
import "./utils/Deploy.sol";
import "./utils/Setup.sol";

contract SidechainGaugesTest is Test, Constants, Deploy, Setup {
    DFX_ public DFX;
    IVeDfx public veDFX;
    IVeBoostProxy public veBoostProxy;
    IGaugeController public gaugeController;
    DfxDistributor public distributor;
    CcipSender public sender;
    MockCcipRouter public router;

    address multisig0 = makeAddr("MULTISIG_0");
    address multisig1 = makeAddr("MULTISIG_1");

    address[] gaugeAddrs = new address[](3);

    function setUp() public {
        // fund multsig
        payable(multisig0).transfer(5e17);

        DFX = deployDfx(1e30);
        veDFX = deployVeDfx(address(DFX));
        veBoostProxy = deployVeBoostProxy(address(veDFX), multisig0);
        gaugeController = deployGaugeController(address(DFX), address(veDFX), multisig0);
        distributor = deployDistributor(address(DFX), address(gaugeController), multisig0, multisig0, multisig1);
        router = deployMockCcipRouter();
        sender = deploySender(address(DFX), address(router), TARGET_CHAIN_SELECTOR, address(0), multisig0, multisig1);

        IERC20 lpt0 = deployLpt("DFX CADC-USDC LP Token", "cadcUsdc");
        IERC20 lpt1 = deployLpt("DFX EUROC-USDC LP Token", "eurocUsdc");
        IERC20 lpt2 = deployLpt("DFX XSGD-USDC LP Token", "xsgdUsdc");

        gaugeAddrs[0] = address(
            deployLiquidityGaugeV4(
                address(DFX),
                address(veDFX),
                address(lpt0),
                address(veBoostProxy),
                address(distributor),
                multisig0,
                multisig1
            )
        );
        gaugeAddrs[1] = address(
            deployLiquidityGaugeV4(
                address(DFX),
                address(veDFX),
                address(lpt1),
                address(veBoostProxy),
                address(distributor),
                multisig0,
                multisig1
            )
        );
        gaugeAddrs[2] = address(
            deployLiquidityGaugeV4(
                address(DFX),
                address(veDFX),
                address(lpt2),
                address(veBoostProxy),
                address(distributor),
                multisig0,
                multisig1
            )
        );

        setupGaugeController(address(gaugeController), gaugeAddrs, multisig0);
        setupDistributor(address(DFX), address(distributor), multisig0, EMISSION_RATE, TOTAL_DFX_REWARDS);

        // Provide sender contract with CCIP gas money
        fundEth(address(sender), 5e17);
    }

    function test_L2GaugeTimetravel() public {
        // epoch 0: do nothing
        assertEq(distributor.miningEpoch(), 0);
        assertEq(DFX.balanceOf(address(distributor)), TOTAL_DFX_REWARDS);

        // epoch 1: distribute rewards to gauges
        vm.warp(block.timestamp + WEEK / WEEK * WEEK);
        vm.prank(multisig0);
        distributor.distributeRewardToMultipleGauges(gaugeAddrs);
        assertEq(distributor.miningEpoch(), 1);

        // epoch 2: deploy L2 gauge, add to gauge controller and distribute rewards
        vm.warp(block.timestamp + WEEK / WEEK * WEEK);
        CcipRootGauge rootGauge = deployRootGauge(
            "L1 ETH/BTC Root Gauge", address(DFX), address(distributor), address(sender), multisig0, multisig1
        );
        // Link mainnet and root gauge addresses
        vm.prank(multisig0);
        sender.setL2Destination(address(rootGauge), MOCK_DESTINATION);
        addToGaugeController(address(gaugeController), address(rootGauge), multisig0, true);

        // set l2 gauge as a delegate for automating distribution by calling RootGauge notifyReward function
        vm.prank(multisig0);
        distributor.setDelegateGauge(address(rootGauge), address(rootGauge), true);
        assertEq(distributor.isInterfaceKnown(address(rootGauge)), true, "Rewards delegate is not set");

        address[] memory allGauges = new address[](4);
        for (uint256 i = 0; i < gaugeAddrs.length; i++) {
            allGauges[i] = gaugeAddrs[i];
        }
        allGauges[3] = address(rootGauge);
        distributor.distributeRewardToMultipleGauges(allGauges);
        assertEq(distributor.miningEpoch(), 2);

        // route gauge receives no immediate rewards
        for (uint256 i = 0; i < gaugeAddrs.length; i++) {
            assertGt(DFX.balanceOf(gaugeAddrs[i]), 0);
        }
        assertEq(DFX.balanceOf(address(rootGauge)), 0);

        // epoch 3: distribute rewards to gauges
        vm.warp(block.timestamp + WEEK / WEEK * WEEK);
        distributor.distributeRewardToMultipleGauges(allGauges);
        assertEq(distributor.miningEpoch(), 3);

        // all gauges received rewards
        for (uint256 i = 0; i < gaugeAddrs.length; i++) {
            assertGt(DFX.balanceOf(gaugeAddrs[i]), 0);
        }
        assertGt(DFX.balanceOf(address(router)), 0);
    }
}
