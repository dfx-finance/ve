// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.7;

interface IVeBoostProxy {
    function admin() external view returns (address);

    function adjusted_balance_of(address _account) external view returns (uint256);

    function commit_admin(address _account) external;

    function accept_transfer_ownership() external;
}