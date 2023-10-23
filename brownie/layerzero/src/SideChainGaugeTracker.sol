// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";

struct Point {
    uint256 bias;
    uint256 slope;
}

contract SideChainGaugeTracker is Ownable {
    event NewGauge(address addr);
    event KilledGauge(address addr);

    // 7 * 86400 seconds - all future times are rounded by week
    // solhint-disable private-vars-leading-underscore
    uint256 constant WEEK = 604800;

    address[1000000000] public gauges;
    uint16 public nGauges;

    // We increment values by 1 prior to storing them here so we can rely on a value
    // of zero as meaning the gauge has not been set; naming from Curve's GaugeController
    mapping(address => int128) public gaugeTypes_;

    // gaugeAddr -> time -> Point
    mapping(address => mapping(uint256 => Point)) public pointsWeight;
    // gaugeAddr -> last scheduled time (next week)
    mapping(address => uint256) public timeWeight;

    // @notice Get gauge type for address
    // @param addr Gauge address
    // @return Gauge type id
    function gaugeTypes(address addr) public view returns (int128) {
        int128 gaugeType = gaugeTypes_[addr];
        assert(gaugeType != 0);
        return gaugeType - 1;
    }

    // @notice Add gauge `addr` of type `gaugeType` with weight `weight`
    // @param addr Gauge address
    // @param gaugeType Gauge type
    function addGauge(address addr, int128 gaugeType) public onlyOwner {
        assert(gaugeTypes_[addr] == 0); // cannot add the same gauge twice

        gauges[nGauges] = addr;
        nGauges += 1;

        gaugeTypes_[addr] = gaugeType + 1;
        emit NewGauge(addr);
    }

    // function _gaugeRelativeWeight(address addr, uint256 time) internal pure returns (uint256) {
    //     // uint256 t = time / WEEK * WEEK;
    //     // uint256 _totalWeight = pointsTotal[t];
    //     // if (_totalWeight > 0) {}
    //     uint256(uint160(addr)) + time;
    //     return 0;
    // }

    // // @notice Get Gauge relative weight (not more than 1.0) normalized to 1e18
    // //         (e.g. 1.0 == 1e18). Inflation which will be received by it is
    // //         inflation_rate * relative_weight / 1e18
    // // @param addr Gauge address
    // // @param time Relative weight at the specified timestamp in the past or present
    // // @return Value of relative weight normalized to 1e18
    // function gaugeRelativeWeight(address addr, uint256 time) public pure returns (uint256) {
    //     return _gaugeRelativeWeight(addr, time);
    // }

    // // @noitce gaugeRelativeWeight with default time of latest block timestamp
    // function gaugeRelativeWeight(address addr) public view returns (uint256) {
    //     return _gaugeRelativeWeight(addr, block.timestamp);
    // }

    // // @notice Get current gauge weight
    // // @param addr Gauge address
    // // @return Gauge weight
    // function getGaugeWeight(address addr) public view returns (uint256) {
    //     return pointsWeight[addr][timeWeight[addr]].bias;
    // }
}
