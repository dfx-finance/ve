// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.19;

import "forge-std/Script.sol";
import "../src/interfaces/IRewardsOnlyGauge.sol";
import "../src/interfaces/IDfxUpgradeableProxy.sol";
import "../src/interfaces/IERC20.sol";

import "./upgrades/IRewardsOnlyGaugeRescue.sol";

contract RecoverClaimSigScript is Script {
    // address polygonGauge = address(0);
    // address polygonRescueContract = address(0);

    address arbitrumGauge = address(0);
    address arbitrumRescueContract = address(0);

    // address multisig = address(0);
    // address proxyAdmin = address(0);
    // address user = address(0);
    // address dfx = address(0);

    function run() external {
        IDfxUpgradeableProxy proxy = IDfxUpgradeableProxy(payable(arbitrumGauge));

        uint256 proxyPrivKey = vm.envUint("PROXY_KEY");
        vm.startBroadcast(proxyPrivKey);
        proxy.upgradeTo(arbitrumRescueContract);
        vm.stopBroadcast();

        // vm.startPrank(multisig);
        // IRewardsOnlyGaugeUpgrade gauge = IRewardsOnlyGaugeUpgrade(polygonGauge);
        // gauge.rescue(address(user));

        // uint256 gaugeAmt = IERC20(gauge.lp_token()).balanceOf(address(gauge));
        // console2.log(gaugeAmt);
        // uint256 amt = IERC20(gauge.lp_token()).balanceOf(user);
        // console2.log(amt);
    }
}
