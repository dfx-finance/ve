// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";

import "../src/layer2/ChildChainRegistry.sol";

import "./utils/Deploy.sol";
import "./utils/Setup.sol";

contract ChildChainRegistryTest is Test, Constants, Deploy, Setup {
    ChildChainRegistry public registry;

    address gaugeImplementation;

    address multisig0 = makeAddr("MULTISIG_0");
    address factory = makeAddr("FACTORY");
    address rootGauge = makeAddr("ROOT_GAUGE");
    address receiver = makeAddr("RECEIVER");
    address newReceiver = makeAddr("NEW_RECEIVER");
    address streamer = makeAddr("STREAMER");
    address childGauge = makeAddr("CHILD_GAUGE");

    function setUp() public {
        registry = deployChildChainRegistry();
        registry.transferOwnership(multisig0);
    }

    function test_AddFactory() public {
        vm.expectRevert("Ownable: caller is not the owner");
        registry.setFactory(factory);

        vm.expectEmit();
        emit ChildChainRegistry.RegisterFactory(factory);

        vm.prank(multisig0);
        registry.setFactory(factory);
    }

    function test_AddGaugeSetAsOwner() public {
        vm.expectRevert("Ownable: caller is not the owner or factory");
        registry.registerGaugeSet(rootGauge, receiver, streamer, childGauge);

        vm.expectEmit();
        emit ChildChainRegistry.RegisterGaugeSet(rootGauge, receiver, streamer, childGauge, block.timestamp);
        vm.prank(multisig0);
        registry.registerGaugeSet(rootGauge, receiver, streamer, childGauge);

        assertEq(registry.nActiveGauges(), 1, "unexpected number of gauges");
    }

    function test_AddGaugeSetAsFactory() public {
        vm.prank(multisig0);
        registry.setFactory(factory);

        vm.expectEmit();
        emit ChildChainRegistry.RegisterGaugeSet(rootGauge, receiver, streamer, childGauge, block.timestamp);
        vm.prank(factory);
        registry.registerGaugeSet(rootGauge, receiver, streamer, childGauge);

        assertEq(registry.nActiveGauges(), 1, "unexpected number of gauges");
    }

    function test_EditGaugeSet() public {
        vm.prank(multisig0);
        registry.registerGaugeSet(rootGauge, receiver, streamer, childGauge);

        vm.expectRevert("Ownable: caller is not the owner");
        registry.editGaugeSet(rootGauge, receiver, streamer, childGauge);

        vm.expectEmit();
        emit ChildChainRegistry.EditGaugeSet(rootGauge, receiver, streamer, childGauge, block.timestamp);
        vm.prank(multisig0);
        registry.editGaugeSet(rootGauge, receiver, streamer, childGauge);

        assertEq(registry.nActiveGauges(), 1, "unexpected number of gauges");
    }

    function test_RemoveGaugeSet() public {
        vm.prank(multisig0);
        registry.registerGaugeSet(rootGauge, receiver, streamer, childGauge);

        vm.expectRevert("Ownable: caller is not the owner");
        registry.unregisterGaugeSet(rootGauge);

        vm.expectEmit();
        emit ChildChainRegistry.UnregisterGaugeSet(rootGauge, receiver, streamer, childGauge);
        vm.prank(multisig0);
        registry.unregisterGaugeSet(rootGauge);

        assertEq(registry.nActiveGauges(), 0, "unexpected number of gauges");
    }
}
