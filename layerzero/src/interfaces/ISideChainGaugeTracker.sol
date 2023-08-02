// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ISideChainGaugeTracker {
    function gaugeTypes(address addr) external view returns (int128);
    function addGauge(address addr, uint16 gaugeType) external;
    function gaugeRelativeWeight(address gaugeAddr) external pure returns (uint256);
    function gaugeRelativeWeight(address gaugeAddr, uint256 time) external view returns (uint256);
}
