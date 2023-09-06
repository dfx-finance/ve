// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {Client} from "@chainlink/contracts-ccip/src/v0.8/ccip/libraries/Client.sol";
import {CCIPReceiver} from "@chainlink/contracts-ccip/src/v0.8/ccip/applications/CCIPReceiver.sol";

import {IChildChainStreamer} from "../interfaces/IChildChainStreamer.sol";

contract ChildChainReceiver is CCIPReceiver {
    // Custom errors to provide more descriptive revert messages.
    error SourceChainNotWhitelisted(uint64 sourceChainSelector); // Used when the source chain has not been whitelisted by the contract owner.
    error SenderNotWhitelisted(address sender); // Used when the sender has not been whitelisted by the contract owner.

    // Event emitted when a message is received from another chain.
    // The unique ID of the CCIP message.
    // The chain selector of the source chain.
    // The address of the sender from the source chain.
    // The text that was received.
    // The token address that was transferred.
    // The token amount that was transferred.
    event MessageReceived(
        bytes32 indexed messageId,
        uint64 indexed sourceChainSelector,
        address sender,
        string text,
        address token,
        uint256 tokenAmount
    );

    address public streamer; // ChildChainStreamer address

    bytes32 private lastReceivedMessageId; // Store the last received messageId.
    address private lastReceivedTokenAddress; // Store the last received token address.
    uint256 private lastReceivedTokenAmount; // Store the last received amount.

    address public admin;

    // Mapping to keep track of whitelisted source chains.
    mapping(uint64 => bool) public whitelistedSourceChains;

    // Mapping to keep track of whitelisted senders.
    mapping(address => bool) public whitelistedSenders;

    /// @dev Modifier that checks whether the msg.sender is admin
    modifier onlyAdmin() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    /// @dev Modifier that checks if the chain with the given sourceChainSelector is whitelisted.
    /// @param _sourceChainSelector The selector of the destination chain.
    modifier onlyWhitelistedSourceChain(uint64 _sourceChainSelector) {
        if (!whitelistedSourceChains[_sourceChainSelector]) {
            revert SourceChainNotWhitelisted(_sourceChainSelector);
        }
        _;
    }

    /// @dev Modifier that checks if the chain with the given sourceChainSelector is whitelisted.
    /// @param _sender The address of the sender.
    modifier onlyWhitelistedSenders(address _sender) {
        if (!whitelistedSenders[_sender]) revert SenderNotWhitelisted(_sender);
        _;
    }

    /// @notice Constructor initializes the contract with the router address.
    /// @param _router The address of the router contract.
    /// @param _streamer The address of associated ChildChainStreamer contract.
    /// @param _admin The address of the contract admin.
    constructor(address _router, address _streamer, address _admin) CCIPReceiver(_router) {
        streamer = _streamer;
        admin = _admin;
    }

    /* Parameters */
    function updateAdmin(address _newAdmin) external onlyAdmin {
        admin = _newAdmin;
    }

    /**
     * @notice Returns the details of the last CCIP received message.
     * @dev This function retrieves the ID, text, token address, and token amount of the last received CCIP message.
     * @return messageId The ID of the last received CCIP message.
     * @return tokenAddress The address of the token in the last CCIP received message.
     * @return tokenAmount The amount of the token in the last CCIP received message.
     */
    function getLastReceivedMessageDetails()
        public
        view
        returns (bytes32 messageId, address tokenAddress, uint256 tokenAmount)
    {
        return (lastReceivedMessageId, lastReceivedTokenAddress, lastReceivedTokenAmount);
    }

    /// handle a received message
    function _ccipReceive(Client.Any2EVMMessage memory message)
        internal
        override
        onlyWhitelistedSourceChain(message.sourceChainSelector) // Make sure source chain is whitelisted
        onlyWhitelistedSenders(abi.decode(message.sender, (address))) // Make sure the sender is whitelisted
    {
        lastReceivedMessageId = message.messageId; // fetch the messageId
        // Expect one token to be transferred at once, but you can transfer several tokens.
        lastReceivedTokenAddress = message.destTokenAmounts[0].token;
        lastReceivedTokenAmount = message.destTokenAmounts[0].amount;

        address rewardToken = message.destTokenAmounts[0].token;
        uint256 rewardAmount = message.destTokenAmounts[0].amount;
        IERC20(rewardToken).transfer(streamer, rewardAmount);
        IChildChainStreamer(streamer).notify_reward_amount(rewardToken);

        emit MessageReceived(
            message.messageId,
            message.sourceChainSelector, // fetch the source chain identifier (aka selector)
            abi.decode(message.sender, (address)), // abi-decoding of the sender address,
            abi.decode(message.data, (string)),
            rewardToken,
            rewardAmount
        );
    }

    /* Admin */
    /// @notice Emergency withdraw
    /// @param _token Address of token to withdraw
    function emergencyWithdraw(address _beneficiary, address _token, uint256 _amount) external onlyAdmin {
        IERC20(_token).transfer(_beneficiary, _amount);
    }

    /// @notice Emergency withdraw native token
    /// @param _beneficiary Receiver of emergeny withdraw
    /// @param _amount Amount to withdraw
    function emergencyWithdrawNative(address _beneficiary, uint256 _amount) external onlyAdmin {
        (bool sent,) = _beneficiary.call{value: _amount}("");
        require(sent, "Failed to send Ether");
    }
}
