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
    IRewardsOnlyGauge public gauge;
    IChildChainStreamer public streamer;
    ChildChainReceiver public receiver;

    address multisig0 = makeAddr("MULTISIG_0");
    address multisig1 = makeAddr("MULTISIG_1");
    address router = address(this);

    function setUp() public {
        DFX = deployDfx(1e30);
        IERC20 lpt = deployLpt("DFX CADC-USDC LP Token", "cadcUsdc");

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
        
    }

    function test_TwoStakers() public {}
}
