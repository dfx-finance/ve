// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";

import "./utils/Deploy.sol";
import "./utils/Payable.sol";
import "./utils/Setup.sol";

contract CcipSenderTest is Test, Deploy, Payable, Setup {
    DFX_ public DFX;
    CcipRootGauge public gauge;
    CcipSender public sender;
    MockCcipRouter public router;

    address multisig0 = makeAddr("MULTISIG_0");
    address multisig1 = makeAddr("MULTISIG_1");

    address destination = makeAddr("FAKE_ADDR");

    function setUp() public {
        DFX = deployDfx(1e30);
        router = deployMockCcipRouter();
        sender = deploySender(address(DFX), address(router), multisig0, multisig1);

        // Set L2 gas token and fee
        vm.prank(multisig0);
        sender.setL2Gas(TARGET_CHAIN_SELECTOR, address(0), 200_000);

        // Link mainnet and root gauge addresses
        vm.prank(multisig0);
        sender.setL2Destination(address(this), destination, TARGET_CHAIN_SELECTOR);

        // Provide sender contract with CCIP gas money
        fundEth(address(sender), 5e17);
    }

    function test_L2GasLimit() public {
        (, uint256 gasLimitFee) = sender.chainFees(TARGET_CHAIN_SELECTOR);
        assertEq(gasLimitFee, 2e5); // default

        vm.expectRevert("Not admin");
        sender.setL2Gas(TARGET_CHAIN_SELECTOR, address(0), 1e7);

        vm.prank(multisig0);
        sender.setL2Gas(TARGET_CHAIN_SELECTOR, address(0), 1e7);
        (, gasLimitFee) = sender.chainFees(TARGET_CHAIN_SELECTOR);
        assertEq(gasLimitFee, 1e7);
    }

    function test_SetAdmin() public {
        assertEq(sender.admin(), multisig0); // default

        vm.expectRevert("Not admin");
        sender.updateAdmin(destination);

        vm.prank(multisig0);
        sender.updateAdmin(destination);
        assertEq(sender.admin(), destination);
    }

    function test_EmergencyWithdrawErc20() public {
        DFX.transfer(address(sender), 1e18);

        vm.expectRevert("Not admin");
        sender.emergencyWithdraw(address(this), address(DFX), 1e18);

        vm.prank(multisig0);
        sender.emergencyWithdraw(address(this), address(DFX), 1e18);
    }

    function test_EmergencyWithdrawEth() public {
        fundEth(address(sender), 1e18);

        vm.expectRevert("Not admin");
        sender.emergencyWithdrawNative(address(this), 1e18);

        vm.prank(multisig0);
        sender.emergencyWithdrawNative(address(this), 1e18);
    }

    function test_RelayRewardZeroAddress() public {
        vm.prank(multisig0);
        sender.setL2Destination(address(this), address(0), TARGET_CHAIN_SELECTOR);

        DFX.approve(address(sender), 2e17);
        vm.expectRevert("No L2 destination");
        sender.relayReward(2e17);
    }

    function test_RelayReward() public {
        DFX.approve(address(sender), 2e17);
        sender.relayReward(2e17);
    }
}
