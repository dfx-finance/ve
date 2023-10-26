// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";

import "../src/interfaces/ILiquidityGaugeV4.sol";

import "./utils/Constants.sol";
import "./utils/Deploy.sol";
import "./utils/Setup.sol";

contract RootGaugeTest is Test, Constants, Deploy, Setup {
    DFX_ public DFX;
    IVeDfx public veDFX;
    IVeBoostProxy public veBoostProxy;
    IGaugeController public gaugeController;
    DfxDistributor public distributor;

    IERC20 public lpt0;
    IERC20 public lpt1;
    IERC20 public lpt2;

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

        lpt0 = deployLpt("DFX CADC-USDC LP Token", "cadcUsdc", address(this));
        lpt1 = deployLpt("DFX EURC-USDC LP Token", "eurcUsdc", address(this));
        lpt2 = deployLpt("DFX XSGD-USDC LP Token", "xsgdUsdc", address(this));

        // Deploy normal gauges to interact with
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
    }

    function test_SingleUserUnboosted() public {
        ILiquidityGaugeV4 gauge = ILiquidityGaugeV4(gaugeAddrs[0]);

        vm.warp(block.timestamp + WEEK / WEEK * WEEK);

        // deposit tokens to gauge
        lpt0.approve(address(gauge), type(uint256).max);
        gauge.deposit(1e18);

        // artificially set gauge weight for our gauge (TBD: needed? why?)
        vm.prank(multisig0);
        gaugeController.change_gauge_weight(address(gauge), 1e18);

        uint256[5] memory expected = [
            uint256(0),
            39696094673618195433600,
            79083866405146632624000,
            118165709965088568384000,
            156944001523561170307200
        ];
        for (uint256 i = 0; i < expected.length; i++) {
            vm.warp(block.timestamp + WEEK / WEEK * WEEK);

            vm.prank(multisig0);
            distributor.distributeRewardToMultipleGauges(gaugeAddrs);
            assertEq(gauge.claimable_reward(address(this), address(DFX)), expected[i]);
        }
    }

    function test_SingleUserClaim() public {
        test_SingleUserUnboosted();

        ILiquidityGaugeV4 gauge = ILiquidityGaugeV4(gaugeAddrs[0]);
        uint256 startingBal = DFX.balanceOf(address(this));

        // claim staking reward
        uint256 rewardAmount = gauge.claimable_reward(address(this), address(DFX));
        gauge.claim_rewards(address(this));
        assertEq(DFX.balanceOf(address(this)) - startingBal, rewardAmount);
    }

    function test_MultiUserBoosted() public {}
}
