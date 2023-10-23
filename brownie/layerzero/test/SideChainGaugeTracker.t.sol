// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/SideChainGaugeTracker.sol";

contract SideChainGaugeTrackerTest is Test {
    SideChainGaugeTracker _gaugeTracker;

    function setUp() public {
        _gaugeTracker = new SideChainGaugeTracker();
    }

    function generateFakeAddr() public view returns (address) {
        return address(bytes20(sha256(abi.encodePacked(block.timestamp))));
    }

    function test_AddGauge() public {
        address fakeAddr = generateFakeAddr();
        _gaugeTracker.addGauge(fakeAddr, 0);

        assert(_gaugeTracker.nGauges() == 1);
        assert(_gaugeTracker.gauges(0) == fakeAddr);
    }
}
