// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IChildChainReceiver {
    function owner() external returns (address _owner);
}
