// SPDX-License-Identifier: MIT
// vyper -f bytecode Test.vy > test_bytecode.txt
// vyper -f bytecode ChildChainStreamer.vy > streamer_bytecode.txt
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";

import "../src/layer2/ChildChainFactory.sol";
import "../src/interfaces/IChildChainReceiver.sol";
import "../src/interfaces/IChildChainStreamer.sol";
import "../src/interfaces/IRewardsOnlyGauge.sol";

import "./utils/Bytecode.sol";
import "./utils/Constants.sol";
import "./utils/Deploy.sol";
import "./utils/Setup.sol";

interface ITest {
    function set(uint256) external;
    function get() external returns (uint256);
    function val() external returns (uint256);
    function owner() external returns (address);
}

contract ChildChainFactoryTest is Test, Constants, Deploy, Setup {
    DFX_ public DFX;
    IERC20 public lpt;
    ChildChainFactory public factory;

    address gaugeImplementation;

    address multisig0 = makeAddr("MULTISIG_0");
    address multisig1 = makeAddr("MULTISIG_1");
    address router = makeAddr("CCIP_ROUTER");
    address rootGauge = makeAddr("ROOT_GAUGE");

    function setUp() public {
        DFX = deployDfx(1e30);
        lpt = deployLpt("DFX CADC-USDC LP Token", "cadcUsdc", address(this));

        // Deploy RewardsOnlyGauge implementation
        gaugeImplementation = vyperDeployer.deployContract("src/layer2/", "RewardsOnlyGauge", "");

        factory = deployChildChainFactory(address(this), Bytecode.streamerBytecode);
    }

    function test_DeployTestContract() public {
        address test = factory._deployVyperContract(Bytecode.testBytecode, abi.encode(456, multisig0));

        ITest(test).set(123);
        assertEq(ITest(test).get(), 123);
    }

    function test_DeployGauge() public {
        (address receiver, address streamer, address gauge) = factory.deployGaugeSet(
            rootGauge, router, gaugeImplementation, address(lpt), multisig0, multisig1, address(DFX)
        );

        assertEq(IChildChainReceiver(receiver).owner(), multisig0);
        assertEq(IChildChainStreamer(streamer).owner(), multisig0);
        assertEq(IRewardsOnlyGauge(gauge).admin(), multisig0);
    }
}
