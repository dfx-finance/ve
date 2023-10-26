// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";

import "../src/mainnet/DfxDistributor.sol";

import "./utils/Constants.sol";
import "./utils/Deploy.sol";
import "./utils/Setup.sol";

contract DfxDistributorTest is Test, Constants, Deploy, Setup {
    DFX_ public DFX;
    IVeDfx public veDFX;
    IVeBoostProxy public veBoostProxy;
    IGaugeController public gaugeController;
    DfxDistributor public distributor;

    address multisig0 = makeAddr("MULTISIG_0");
    address multisig1 = makeAddr("MULTISIG_1");

    function setUp() public {
        vm.warp(1697932800); // Oct 21, 2023 @ 00:00:00 UTC

        DFX = deployDfx(1e30);
        veDFX = deployVeDfx(address(DFX));
        veBoostProxy = deployVeBoostProxy(address(veDFX), multisig0);
        gaugeController = deployGaugeController(address(DFX), address(veDFX), multisig0);
        distributor = deployDistributor(address(DFX), address(gaugeController), multisig0, multisig0, multisig1);
    }

    function test_EpochStart() public {
        assertEq(distributor.startEpochTime(), 1697673600); // Oct 19, 2023 @ 00:00:00 UTC
    }

    function test_EarlyDistribution() public {}
}
