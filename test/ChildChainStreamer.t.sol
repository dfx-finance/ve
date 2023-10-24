// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";

import "../src/interfaces/IChildChainStreamer.sol";
import "../src/interfaces/IRewardsOnlyGauge.sol";

import "./utils/Constants.sol";
import "./utils/Deploy.sol";
import "./utils/Setup.sol";

contract ChildChainStreamerTest is Test, Constants, Deploy, Setup {
    DFX_ public DFX;
    IERC20 public lpt;
    IRewardsOnlyGauge public gauge;
    IChildChainStreamer public streamer;
    ChildChainReceiver public receiver;

    address multisig0 = makeAddr("MULTISIG_0");
    address multisig1 = makeAddr("MULTISIG_1");
    address router = address(this);
    address user = makeAddr("USER");

    function setUp() public {
        DFX = deployDfx(1e30);
        lpt = deployLpt("DFX CADC-USDC LP Token", "cadcUsdc", address(this));

        gauge = deployRewardsOnlyGauge(address(lpt), multisig0, multisig1);
        streamer = deployChildChainStreamer(address(DFX), address(gauge), multisig0);
        receiver = deployChildChainReceiver(router, address(streamer), multisig0);
    }

    function test_ReceiveRewardsCcip() public {
        // update authorized user for childchainstreamer rewards
        // DEV: This will be the address of the CCTP contract which is calling "notify_reward_amount" on ChildChainStreamer
        vm.prank(multisig0);
        streamer.set_reward_distributor(address(this), address(receiver));

        sendToken(address(DFX), 1e23, address(this), address(streamer));

        streamer.notify_reward_amount(address(DFX));

        // check that token distribution/second will equal the total rewards
        // provided for the epoch
        IChildChainStreamer.RewardToken memory data = streamer.reward_data(address(DFX));
        assertApproxEqRel(data.rate * WEEK, 1e23, 1e14); // 99.99%
    }

    function test_StreamToGauge() public {
        setL2GaugeReward(address(gauge), address(streamer), router, address(DFX), multisig0);

        // give distributor rewards
        sendToken(address(DFX), 1e23, address(this), address(streamer));
        streamer.notify_reward_amount(address(DFX));

        // deposit lpt to l2 gauge
        lpt.transfer(user, 1e18);
        vm.startPrank(user);
        lpt.approve(address(gauge), type(uint256).max);
        gauge.deposit(1e18);
        vm.stopPrank();

        assertEq(gauge.balanceOf(address(user)), 1e18);
        assertEq(gauge.reward_tokens(0), address(DFX));

        for (uint256 i = 0; i < 3; i++) {
            vm.warp(block.timestamp + WEEK / WEEK * WEEK);
            sendToken(address(DFX), 1e23, address(this), address(streamer));
            streamer.notify_reward_amount(address(DFX));

            // DFX balances ~= 1e23
            assertApproxEqAbs(DFX.balanceOf(address(streamer)), 1e23, 1e8);
            assertApproxEqAbs(DFX.balanceOf(address(gauge)), 1e23, 1e8);

            // Claim rewards
            uint256 availableRewards = gauge.claimable_reward_write(user, address(DFX));
            vm.prank(user);
            gauge.claim_rewards(user);
            uint256 claimedRewards = gauge.claimed_reward(user, address(DFX));

            // User staked LPT
            assertEq(gauge.balanceOf(user), 1e18);
            // User available rewards
            assertApproxEqAbs(availableRewards, 1e23, 1e8);
            // User claimed rewards
            assertApproxEqAbs(claimedRewards, (i + 1) * 1e23, 1e18);
            // User DFX balance
            assertApproxEqAbs(DFX.balanceOf(user), (i + 1) * 1e23, 1e18);
        }
    }

    function test_TwoStakers() public {}
}
