// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract Constants {
    uint256 WEEK = 86400 * 7;

    uint256 EMISSION_RATE = 2e17;
    uint256 TOTAL_DFX_REWARDS = 1_000_000 * 1e18;

    uint256 TARGET_CHAIN_SELECTOR = 14767482510784806043;
    address MOCK_DESTINATION = 0x33Af579F8faFADa29d98922A825CFC0228D7ce39;
}
