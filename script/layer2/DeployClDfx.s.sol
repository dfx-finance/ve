// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.19;

import {Script, console2} from "forge-std/Script.sol";

import "../../src/DfxUpgradeableProxy.sol";
import "../../src/cldfx/clDFX.sol";

contract DeployClDfxScript is Script {
    function setUp() public {}

    function run() public {
        address deployProxyAcct = makeAddr("deployProxy");

        vm.startBroadcast();
        // Deploy implementation
        clDFX dfx = new clDFX();

        // Deploy proxy
        bytes memory params = abi.encode("DFX Token (L2)", "DFX", address(0), "0.0.1");
        DfxUpgradeableProxy proxy = new DfxUpgradeableProxy(address(dfx), deployProxyAcct, params);
        console2.log(address(proxy));
        vm.stopBroadcast();
    }
}
