// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";

import "../src/mainnet/DfxDistributor.sol";

import "./utils/Constants.sol";
import "./utils/Deploy.sol";
import "./utils/Setup.sol";

contract DfxDistributorTest is Test, Constants, Deploy, Setup {
    DFX_ public DFX;
    IERC20 public lpt;
    IVeDfx public veDFX;
    IVeBoostProxy public veBoostProxy;
    IGaugeController public gaugeController;
    DfxDistributor public distributor;
    ILiquidityGaugeV4 public gauge;

    address multisig0 = makeAddr("MULTISIG_0");
    address multisig1 = makeAddr("MULTISIG_1");

    function setUp() public {
        vm.warp(1697932800); // Oct 21, 2023 @ 00:00:00 UTC

        // deploy contracts
        DFX = deployDfx(1e30);
        lpt = deployLpt("DFX CADC-USDC LP Token", "cadcUsdc", address(this));
        veDFX = deployVeDfx(address(DFX));
        veBoostProxy = deployVeBoostProxy(address(veDFX), multisig0);
        gaugeController = deployGaugeController(address(DFX), address(veDFX), multisig0);
        distributor = deployDistributor(address(DFX), address(gaugeController), multisig0, multisig0, multisig1);
        gauge = deployLiquidityGaugeV4(
            address(DFX),
            address(veDFX),
            address(lpt),
            address(veBoostProxy),
            address(distributor),
            multisig0,
            multisig1
        );

        // initialize VE
        address[] memory gaugeAddrs = new address[](1);
        gaugeAddrs[0] = address(gauge);
        setupGaugeController(address(gaugeController), gaugeAddrs, multisig0);
        setupDistributor(address(DFX), address(distributor), multisig0, EMISSION_RATE, TOTAL_DFX_REWARDS);
    }

    function test_EpochStart() public {
        assertEq(distributor.startEpochTime(), 1697673600); // Oct 19, 2023 @ 00:00:00 UTC
    }

    function test_EarlyDistribution() public {
        assertEq(distributor.miningEpoch(), 0, "Unexpected epoch");

        // check that we have been pre-minted LP tokens
        assertEq(lpt.balanceOf(address(this)), 1_000_000_000 * 1e18);

        // deposit tokens to L1 gauge
        lpt.approve(address(gauge), type(uint256).max);
        gauge.deposit(1e18);

        vm.warp(block.timestamp + 10);

        distributor.distributeReward(address(gauge));
        assertEq(distributor.miningEpoch(), 0, "Unexpected epoch");
        assertEq(DFX.balanceOf(address(gauge)), 0, "Gauge received rewards before first epoch");
    }
}
