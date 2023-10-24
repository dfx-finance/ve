// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

import "../../src/interfaces/IGaugeController.sol";
import "../../src/mainnet/DfxDistributor.sol";

contract Setup is Test {
    int128 defaultGaugeType = 0;
    uint256 defaultGaugeTypeWeight = 1e18;

    function fundEth(address target, uint256 amount) public {
        (bool success,) = address(target).call{value: amount}("");
        require(success, "failed to fund");
    }

    function sendToken(address token, uint256 amount, address from, address to) public {
        vm.prank(from);
        IERC20(token).transfer(to, amount);
    }

    function setupGaugeController(address gaugeController, address[] memory gaugeAddrs, address admin) public {
        vm.startPrank(admin);
        IGaugeController(gaugeController).add_type("AMM Liquidity Pools", defaultGaugeTypeWeight);

        for (uint256 i = 0; i < gaugeAddrs.length; i++) {
            IGaugeController(gaugeController).add_gauge(gaugeAddrs[i], defaultGaugeType, defaultGaugeTypeWeight);
        }
        vm.stopPrank();
    }

    function setupDistributor(address DFX, address distributor, address admin, uint256 rate, uint256 totalRewardsAmount)
        public
    {
        // Distribute rewards to the distributor contract
        sendToken(DFX, totalRewardsAmount, address(this), distributor);

        vm.startPrank(admin);
        // Set rate to distribute 1,000,000 rewards (see spreadsheet)
        DfxDistributor(distributor).setRate(rate);

        // Turn on distributions to gauges
        DfxDistributor(distributor).toggleDistributions();
        vm.stopPrank();
    }

    function addToGaugeController(address gaugeController, address gauge, address admin, bool addPlaceholder) public {
        vm.startPrank(admin);
        if (addPlaceholder) {
            IGaugeController(gaugeController).add_type("DFX Perpetuals", 0);
        }

        // add new l2 gauge type to gauge controller
        IGaugeController(gaugeController).add_type("L2 Liquidity Pools", 1e18);

        // add l2 gauge to gauge controller
        IGaugeController(gaugeController).add_gauge(gauge, 2, defaultGaugeTypeWeight);
        vm.stopPrank();
    }

    function setL2GaugeReward(address gauge, address streamer, address token, address admin) public {
        
    }
}
