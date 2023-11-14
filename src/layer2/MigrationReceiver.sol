// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {Client} from "@chainlink/contracts-ccip/src/v0.8/ccip/libraries/Client.sol";
import {CCIPReceiver} from "../vendor/chainlink/CCIPReceiver.sol";

contract MigrationReceiver is CCIPReceiver {
    // Event emitted when a message is received from another chain.
    // The unique ID of the CCIP message.
    // The chain selector of the source chain.
    // The address of the sender from the source chain.
    // The text that was received.
    // The token address that was transferred.
    // The token amount that was transferred.
    event RewardReceived(
        bytes32 indexed messageId,
        uint64 indexed sourceChainSelector,
        address sender,
        address token,
        uint256 tokenAmount
    );

    bytes32 private lastReceivedMessageId; // Store the last received messageId.
    address private lastReceivedTokenAddress; // Store the last received token address.
    uint256 private lastReceivedTokenAmount; // Store the last received amount.

    address public owner;

    // Custom errors to provide more descriptive revert messages.
    error SourceChainNotWhitelisted(uint64 sourceChainSelector); // Used when the source chain has not been whitelisted by the contract owner.
    error SenderNotWhitelisted(address sender); // Used when the sender has not been whitelisted by the contract owner.

    // Mapping to keep track of whitelisted source chains.
    uint64 public whitelistedSourceChain;
    address public whitelistedSender;

    /// @dev Modifier that checks if the chain with the given sourceChainSelector is whitelisted.
    /// @param _sourceChainSelector The selector of the destination chain.
    modifier onlyWhitelistedSourceChain(uint64 _sourceChainSelector) {
        if (whitelistedSourceChain != _sourceChainSelector) {
            revert SourceChainNotWhitelisted(_sourceChainSelector);
        }
        _;
    }

    /// @dev Modifier that checks if the chain with the given sourceChainSelector is whitelisted.
    /// @param _sender The address of the sender.
    modifier onlyWhitelistedSenders(address _sender) {
        if (whitelistedSender != _sender) revert SenderNotWhitelisted(_sender);
        _;
    }

    /// @dev Modifier that checks whether the msg.sender is owner
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor(address _router, uint64 _sourceChain, address _sender, address _owner) CCIPReceiver(_router) {
        whitelistedSourceChain = _sourceChain;
        whitelistedSender = _sender;
        owner = _owner;
    }

    /// handle a received message
    function _ccipReceive(Client.Any2EVMMessage memory message)
        internal
        override
        onlyWhitelistedSourceChain(message.sourceChainSelector)
        onlyWhitelistedSenders(abi.decode(message.sender, (address)))
    {
        lastReceivedMessageId = message.messageId; // fetch the messageId
        // Expect one token to be transferred at once, but you can transfer several tokens.
        address rewardToken = message.destTokenAmounts[0].token;
        uint256 rewardAmount = message.destTokenAmounts[0].amount;
        lastReceivedTokenAddress = rewardToken;
        lastReceivedTokenAmount = rewardAmount;

        // Send received tokens to owner
        IERC20(rewardToken).transfer(owner, rewardAmount);

        emit RewardReceived(
            message.messageId,
            message.sourceChainSelector, // fetch the source chain identifier (aka selector)
            abi.decode(message.sender, (address)), // abi-decoding of the sender address,
            rewardToken,
            rewardAmount
        );
    }

    /* Admin */
    /// @notice Fallback function to allow the contract to receive Ether.
    /// @dev This function has no function body, making it a default function for receiving Ether.
    /// It is automatically called when Ether is transferred to the contract without any data.
    receive() external payable {}

    /// @notice Emergency withdraw
    /// @param _token Address of token to withdraw
    function emergencyWithdraw(address _beneficiary, address _token, uint256 _amount) external onlyOwner {
        IERC20(_token).transfer(_beneficiary, _amount);
    }

    /// @notice Emergency withdraw native token
    /// @param _beneficiary Receiver of emergeny withdraw
    /// @param _amount Amount to withdraw
    function emergencyWithdrawNative(address _beneficiary, uint256 _amount) external onlyOwner {
        (bool sent,) = _beneficiary.call{value: _amount}("");
        require(sent, "Failed to send Ether");
    }
}
