// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Script.sol";

import "../src/mainnet/prev/CcipRootGauge0.sol";
import "../src/mainnet/prev/CcipSender0.sol";
import "../src/mainnet/CcipRootGauge.sol";
import "../src/mainnet/CcipSender.sol";
import "../src/interfaces/IDfxUpgradeableProxy.sol";

contract RootGaugeSendingTest is Script {
    address public dfx = 0x888888435FDe8e7d4c54cAb67f206e4199454c60;
    address public distributor = 0xD3E7444d5DB4dDF0F9A1B52d62367C339B7bE8A9;
    address public multisig0 = 0x27E843260c71443b4CC8cB6bF226C3f77b9695AF;
    address public multisig1 = 0x26f539A0fE189A7f228D7982BF10Bc294FA9070c;
    address public proxyAdmin = 0x9aDa42ed163bB45ea2FF11c06c59cF27d27E6cba;
    address public cadcUsdcGauge = 0x037A88165821210756800cA174c8cB723c665b47;
    address public ccipSender = 0x7ace867b3a503C6C76834ac223993FBD8963BED2;

    // uint256 privKey = vm.envUint("PRIVKEY");

    function run() public {
        // // new implementations
        // vm.broadcast(privKey);
        // CcipRootGauge gaugeImpl = new CcipRootGauge(dfx);

        CcipRootGauge gauge = CcipRootGauge(0x037A88165821210756800cA174c8cB723c665b47);
        console2.log(address(gauge.sender()));
        // console2.log(gaugeImpl.DFX());

        // CcipSender senderImpl = new CcipSender(dfx);

        // // upgrade root gauge
        // IDfxUpgradeableProxy gaugeProxy = IDfxUpgradeableProxy(cadcUsdcGauge);
        // vm.prank(multisig1);
        // gaugeProxy.upgradeTo(address(gaugeImpl));

        // // upgrade sender
        // IDfxUpgradeableProxy senderProxy = IDfxUpgradeableProxy(ccipSender);
        // vm.prank(proxyAdmin);
        // senderProxy.upgradeTo(address(senderImpl));

        // // call contracts
        // CcipRootGauge gauge = CcipRootGauge(cadcUsdcGauge);

        // vm.prank(multisig0);
        // gauge.setDistributor(multisig0);

        // CcipRootGauge gauge = CcipRootGauge(cadcUsdcGauge);
        // console2.log(gauge.admin());
        // vm.prank(proxyAdmin);
        // console2.log(gaugeProxy.getAdmin());
        // console2.log(address(gauge.sender()));

        // vm.prank(multisig0);
        // gauge.setSender(ccipSender);

        // vm.prank(distributor);
        // gauge.notifyReward(4704634728990992338200);

        // vm.prank(distributor);
        // gauge.notifyReward(0);

        // // console2.log(address(gauge.sender()));

        // // (address dst, uint64 selector) = sender.destinations(cadcUsdcGauge);
        // // console2.log(dst);
    }
}
