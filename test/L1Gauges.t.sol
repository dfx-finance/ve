// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";

import "../src/interfaces/ILiquidityGaugeV4.sol";

import "./utils/Constants.sol";
import "./utils/Deploy.sol";
import "./utils/Setup.sol";

contract L1GaugesTest is Test, Constants, Deploy, Setup {
    DFX_ public DFX;
    IVeDfx public veDFX;
    IVeBoostProxy public veBoostProxy;
    IGaugeController public gaugeController;
    DfxDistributor public distributor;
    SmartWalletChecker public checker;

    IERC20LP public lpt0;
    IERC20LP public lpt1;
    IERC20LP public lpt2;

    address multisig0 = makeAddr("MULTISIG_0");
    address multisig1 = makeAddr("MULTISIG_1");
    address user0 = makeAddr("USER_0");
    address user1 = makeAddr("USER_1");

    address[] gaugeAddrs = new address[](3);

    function setUp() public {
        // dev: advance 1 week to prevent initial DfxDistributor timestamp getting rounded to 0.
        // This will cause it to fail by trying to safeApprove() the reward token twice.
        vm.warp(block.timestamp / WEEK * WEEK + WEEK);

        // fund multsig
        payable(multisig0).transfer(5e17);

        DFX = deployDfx(1e30);
        veDFX = deployVeDfx(address(DFX));
        veBoostProxy = deployVeBoostProxy(address(veDFX), multisig0);
        gaugeController = deployGaugeController(address(DFX), address(veDFX), multisig0);
        distributor = deployDistributor(address(DFX), address(gaugeController), multisig0, multisig0, multisig1);
        checker = deploySmartWalletChecker();

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

        veDFX.commit_smart_wallet_checker(address(checker));
        veDFX.apply_smart_wallet_checker();

        setupGaugeController(address(gaugeController), gaugeAddrs, multisig0);
        setupDistributor(address(DFX), address(distributor), multisig0, EMISSION_RATE, TOTAL_DFX_REWARDS);
    }

    function test_SingleUserUnboosted() public {
        ILiquidityGaugeV4 gauge = ILiquidityGaugeV4(gaugeAddrs[0]);

        vm.warp(block.timestamp / WEEK * WEEK + WEEK);

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
            vm.warp(block.timestamp / WEEK * WEEK + WEEK);

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

    function test_MultiUserBoosted() public {
        ILiquidityGaugeV4 gauge = ILiquidityGaugeV4(gaugeAddrs[1]);

        // mint 10,000 LPT
        lpt1.mint(user0, 1e22);
        lpt1.mint(user1, 1e22);

        // deposit lpt to gauge
        vm.prank(user0);
        lpt1.approve(address(gauge), 1e22);
        vm.prank(user0);
        gauge.deposit(1e22);

        vm.prank(user1);
        lpt1.approve(address(gauge), 1e22);
        vm.prank(user1);
        gauge.deposit(1e22);

        assertEq(distributor.miningEpoch(), 0);

        // epoch 1: set chain start of epoch 1 and distribute available reward to gauges
        vm.warp(block.timestamp / WEEK * WEEK + WEEK);
        vm.prank(multisig0);
        distributor.distributeRewardToMultipleGauges(gaugeAddrs);
        assertEq(distributor.miningEpoch(), 1);

        // epoch 1: advance chain to 5h10s before epoch 1-to-2 change
        vm.warp(block.timestamp / WEEK * WEEK + WEEK - 5 * 60 * 60 - 10);
        assertEq(distributor.miningEpoch(), 1);

        // mint 250,000 DFX
        DFX.mint(user0, 250_000e18);

        // lock 1,000 DFX for 100 epochs
        vm.prank(user0);
        DFX.approve(address(veDFX), 1_000e18);
        vm.prank(user0);
        veDFX.create_lock(1_000e18, block.timestamp + 100 * WEEK);

        // submit ve vote
        uint256[3] memory gaugeWeights = [uint256(0), 10000, 0];
        for (uint256 i = 0; i < gaugeAddrs.length; i++) {
            vm.prank(user0);
            gaugeController.vote_for_gauge_weights(gaugeAddrs[i], gaugeWeights[i]);
        }

        // all voting power is registered on controller
        assertEq(gaugeController.vote_user_power(user0), 10000);

        vm.prank(user0);
        gauge.user_checkpoint(user0);
        uint256 rewardsDiff0 = gauge.claimable_reward(user0, address(DFX)) - gauge.claimable_reward(user1, address(DFX));

        // epoch 1: advance chain to 1h10s before epoch 1-to-2 change
        vm.warp(block.timestamp + 4 * 60 * 60);

        // checkpoint for calculating boost
        vm.prank(user0);
        gauge.user_checkpoint(user0);
        uint256 rewardsDiff1 = gauge.claimable_reward(user0, address(DFX)) - gauge.claimable_reward(user1, address(DFX));

        // check that boost is enabled for user0
        assertGt(rewardsDiff1, rewardsDiff0);
        assertEq(distributor.miningEpoch(), 1);

        // epoch 2
        vm.warp(block.timestamp / WEEK * WEEK + WEEK);

        // test next 5 epochs between naked and boosted rewards
        // 1. rewards are not claimed between rounds during test and therefore expected to accumulate
        // 2. expected rewards floored to nearest int value (whole DFX tokens) to allow for small variation between mining times
        uint256[5] memory expected0 = [
            uint256(20258702920369226864000), // epoch 0 + epoch 1 rewards (mining epoch 2)
            104965595372037993104000,
            189010978932716389704000,
            272399946591783154144000,
            355137550452363291084000
        ];
        uint256[5] memory expected1 = [
            uint256(19748128211829754328000),
            53630885192497260824000,
            87249038616768619464000,
            120604625680395325240000,
            153699667224627380016000
        ];
        for (uint256 i = 0; i < 5; i++) {
            vm.prank(multisig0);
            distributor.distributeRewardToMultipleGauges(gaugeAddrs);
            assertEq(distributor.miningEpoch(), i + 2);

            // checkpoint for calculating boost
            vm.prank(user0);
            gauge.user_checkpoint(user0);
            vm.prank(user1);
            gauge.user_checkpoint(user1);

            assertEq(gauge.claimable_reward(user0, address(DFX)), expected0[i]);
            assertEq(gauge.claimable_reward(user1, address(DFX)), expected1[i]);

            vm.warp(block.timestamp / WEEK * WEEK + WEEK);
        }
    }
}
