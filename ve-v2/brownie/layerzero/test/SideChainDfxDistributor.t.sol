// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "@openzeppelin/contracts/proxy/transparent/TransparentUpgradeableProxy.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";

import "../src/SideChainDfxDistributor.sol";
import "../src/SideChainGaugeTracker.sol";
import "../src/mocks/Erc20Mock.sol";

contract SideChainDfxDistributorTest is Test {
    address thisAddr = address(this);
    address deployAddr = vm.addr(1);

    ERC20 _rewardToken;
    SideChainGaugeTracker _gaugeTracker;
    SideChainDfxDistributor _distributor;

    function setUp() public {
        _rewardToken = new MockERC20("FakeDFX", "FDFX", 1e24);
        _gaugeTracker = new SideChainGaugeTracker();

        vm.startPrank(deployAddr);
        // Deploy the Distributor implementation
        SideChainDfxDistributor distributorImplementation = new SideChainDfxDistributor();

        // Deploy the proxy contract
        TransparentUpgradeableProxy proxy = new TransparentUpgradeableProxy(
            address(distributorImplementation), address(this), ""
        );

        // Cast proxy contract to the SideChainDfxDistributor type
        _distributor = SideChainDfxDistributor(payable(address(proxy)));
        _distributor.initialize(address(_rewardToken), address(_gaugeTracker), thisAddr, thisAddr);
        vm.stopPrank();
    }

    function test_ActiveGauges() public view {}

    function test_KilledGauges() public {}
    function test_PassThroughRewards() public {}
    function test_EmergencyWithdraw() public {}
    function test_ReplaceDistributor() public {}
    function test_NewGuardian() public {}
    function test_NewGovernor() public {}
}
