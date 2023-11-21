// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.19;

import "forge-std/Script.sol";
import "../src/interfaces/IRewardsOnlyGauge.sol";

contract RecoverClaimSigScript is Script {
    address polygonStreamer = 0xfA707fD6c519adA3995B9358774b4289114dB534;
    address polygonGauge = 0xf0453d9642Df3e2fD46e7046D7A90F05702BF9dd;

    address multisig = 0x80D27bfb638F4Fea1e862f1bd07DEa577CB77D38;
    address user = 0xde0223237AE9776a0654fdA6816cDAC50eDd72B5;
    address dfx = 0x27f485b62C4A7E635F561A87560Adf5090239E93;

    function run() external {
        IRewardsOnlyGauge gauge = IRewardsOnlyGauge(0xf0453d9642Df3e2fD46e7046D7A90F05702BF9dd);
        console2.log(gauge.admin());

        address[8] memory rewards =
            [dfx, address(0), address(0), address(0), address(0), address(0), address(0), address(0)];
        bytes4 sig = bytes4(keccak256("get_reward()"));
        vm.prank(multisig);
        gauge.set_rewards(polygonStreamer, sig, rewards);
    }
}
