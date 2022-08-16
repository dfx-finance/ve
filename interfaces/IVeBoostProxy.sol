// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.7;

interface VotingEscrowBoost {
    function adjusted_balance_of(address _account) external view returns (uint256);
}