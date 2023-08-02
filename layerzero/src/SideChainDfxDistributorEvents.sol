// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./interfaces/IGaugeController.sol";

/// @title SideChainDfxDistributorEvents
/// @author DFX Finance, Angle Protocol
/// @notice All the events used in `SideChainDfxDistributor` contract
contract SideChainDfxDistributorEvents {
    event UpdateMiningParameters(uint256 time, uint256 rate, uint256 supply);
    event GaugeToggled(address indexed gaugeAddr, bool newStatus);
    event RewardDistributed(address indexed gaugeAddr, uint256 rewardTally);
}
