// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.7;

interface IVeBoostProxy {
    function adjusted_balance_of(address _account) external view returns (uint256);
}