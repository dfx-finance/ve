// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Script, console2} from "forge-std/Script.sol";
import {Test} from "forge-std/Test.sol";

import "../../src/DfxUpgradeableProxy.sol";
import "../../src/mainnet/CcipSender.sol";

contract DeploySender is Script, Test {
    address public DFX = 0x888888435FDe8e7d4c54cAb67f206e4199454c60;
    address public router = 0xE561d5E02207fb5eB32cca20a699E0d8919a1476;
    address public multisig0 = 0x4CFAB93A974397786d2D323E7681dF7213c8124e;
    address public deployProxyAcct = 0x9aDa42ed163bB45ea2FF11c06c59cF27d27E6cba;

    function setUp() public {}

    function run() public {
        uint256 privKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(privKey);
        // Deploy implementation
        CcipSender _sender = new CcipSender(DFX);
        // Deploy proxy
        bytes memory params = abi.encodeWithSelector(CcipSender.initialize.selector, router, multisig0);
        DfxUpgradeableProxy proxy = new DfxUpgradeableProxy(address(_sender), deployProxyAcct, params);
        vm.stopBroadcast();
    }
}
