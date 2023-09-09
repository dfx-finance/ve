// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {Client} from "@chainlink/contracts-ccip/src/v0.8/ccip/libraries/Client.sol";
import {CCIPReceiver} from "../vendor/chainlink/CCIPReceiver.sol";

contract CCIPDemo is CCIPReceiver {
    constructor(address _router) CCIPReceiver(_router) {}

    function _ccipReceive(Client.Any2EVMMessage memory message) internal override {}

    /// @notice Fallback function to allow the contract to receive Ether.
    /// @dev This function has no function body, making it a default function for receiving Ether.
    /// It is automatically called when Ether is transferred to the contract without any data.
    receive() external payable {}
}
