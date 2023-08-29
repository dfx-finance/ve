// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./IERC20.sol";

struct EVMTokenAmount {
    address token; // token address on the local chain.
    uint256 amount; // Amount of tokens.
}

// If extraArgs is empty bytes, the default is 200k gas limit and strict = false.
struct EVM2AnyMessage {
    bytes receiver; // abi.encode(receiver address) for dest EVM chains
    bytes data; // Data payload
    EVMTokenAmount[] tokenAmounts; // Token transfers
    address feeToken; // Address of feeToken. address(0) means you will send msg.value.
    bytes extraArgs; // Populate this with _argsToBytes(EVMExtraArgsV1)
}

contract MockCcipRouter {
    constructor() {}

    function getFee(uint256 chainSelector, EVM2AnyMessage calldata message) public pure returns (uint256) {
        chainSelector;
        message;
        return 1e18;
    }

    function ccipSend(uint256 chainSelector, EVM2AnyMessage calldata message) public payable {
        if (message.feeToken == address(0)) {
            uint256 feeAmount = getFee(chainSelector, message);
            IERC20(message.feeToken).transferFrom(msg.sender, address(this), feeAmount);
        }

        // Transfer the tokens to the token pools.
        for (uint256 i = 0; i < message.tokenAmounts.length; ++i) {
            IERC20 token = IERC20(message.tokenAmounts[i].token);
            token.transferFrom(msg.sender, address(this), message.tokenAmounts[i].amount);
        }
    }
}
