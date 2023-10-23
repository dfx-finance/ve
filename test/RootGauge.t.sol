// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";

import "./utils/Deploy.sol";
import "./utils/Setup.sol";

contract RootGaugeTest is Test, Deploy, Setup {
    DFX_ public DFX;
    IVeDfx public veDFX;
    IVeBoostProxy public veBoostProxy;
    CcipRootGauge public gauge;
    CcipSender public sender;
    MockCcipRouter public router;

    address multisig0 = makeAddr("MULTISIG_0");
    address multisig1 = makeAddr("MULTISIG_1");

    function setUp() public {
        DFX = deployDfx(1e30);
        veDFX = deployVeDfx(address(DFX));
        veBoostProxy = deployVeBoostProxy(address(veDFX), multisig0);
        router = deployMockCcipRouter();
        sender = deploySender(address(DFX), address(router), TARGET_CHAIN_SELECTOR, address(0), multisig0, multisig1);

        gauge = deployRootGauge(
            "DFX BTC/ETH Root Gauge",
            address(DFX),
            address(this), // distributor
            address(sender),
            multisig0,
            multisig1
        );

        // Link mainnet and root gauge addresses
        vm.prank(multisig0);
        sender.setL2Destination(address(gauge), MOCK_DESTINATION);

        // Provide sender contract with CCIP gas money
        fundEth(address(sender), 5e17);
    }

    function test_RewardsForwarding() public {
        sendToken(address(DFX), 1000e18, address(this), address(gauge));
        gauge.notifyReward(1000e18);
    }
}
