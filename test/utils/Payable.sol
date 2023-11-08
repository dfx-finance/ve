// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract Payable {
    /// @notice Fallback function to allow the contract to receive Ether.
    /// @dev This function has no function body, making it a default function for receiving Ether.
    /// It is automatically called when Ether is transferred to the contract without any data.
    receive() external payable {}
}
