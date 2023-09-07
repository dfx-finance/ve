// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {Client} from "@chainlink/contracts-ccip/src/v0.8/ccip/libraries/Client.sol";
import {CCIPReceiver} from "../vendor/chainlink/CCIPReceiver.sol";

import {IChildChainStreamer} from "../../interfaces/IChildChainStreamer.sol";

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

    address public owner;

    // Mapping to keep track of whitelisted source chains.
    mapping(uint64 => bool) public whitelistedSourceChains;

    // Mapping to keep track of whitelisted senders.
    mapping(address => bool) public whitelistedSenders;

    /// @dev Modifier that checks whether the msg.sender is owner
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
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
    /// @param _owner The address of the contract owner.
    constructor(address _router, address _streamer, address _owner) CCIPReceiver(_router) {
        streamer = _streamer;
        owner = _owner;
    }

    /* Parameters */
    function updateOwner(address _newOwner) external onlyOwner {
        owner = _newOwner;
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
    function _ccipReceive(Client.Any2EVMMessage memory message) internal override {
        lastReceivedMessageId = message.messageId; // fetch the messageId
        // Expect one token to be transferred at once, but you can transfer several tokens.
        address rewardToken = message.destTokenAmounts[0].token;
        uint256 rewardAmount = message.destTokenAmounts[0].amount;
        lastReceivedTokenAddress = rewardToken;
        lastReceivedTokenAmount = rewardAmount;

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

    /* Tests */
    function testBuildCcipMessage(address _receiver, address _token, uint256 _amount, address _feeTokenAddress)
        public
        pure
        returns (Client.EVM2AnyMessage memory)
    {
        // Set the token amounts
        Client.EVMTokenAmount[] memory tokenAmounts = new Client.EVMTokenAmount[](1);
        Client.EVMTokenAmount memory tokenAmount = Client.EVMTokenAmount({token: _token, amount: _amount});
        tokenAmounts[0] = tokenAmount;
        // Create an EVM2AnyMessage struct in memory with necessary information for sending a cross-chain message
        Client.EVM2AnyMessage memory evm2AnyMessage = Client.EVM2AnyMessage({
            receiver: abi.encode(_receiver), // ABI-encoded receiver address
            data: "", // No data
            tokenAmounts: tokenAmounts, // The amount and type of token being transferred
            extraArgs: Client._argsToBytes(
                // Additional arguments, setting gas limit to 0 as we are not sending any data and non-strict sequencing mode
                Client.EVMExtraArgsV1({gasLimit: 0, strict: false})
                ),
            // Set the feeToken to a feeTokenAddress, indicating specific asset will be used for fees
            feeToken: _feeTokenAddress
        });
        return evm2AnyMessage;
    }

    /// handle a received message
    function testCcipReceive(Client.Any2EVMMessage memory message) public {
        lastReceivedMessageId = message.messageId; // fetch the messageId
        // Expect one token to be transferred at once, but you can transfer several tokens.
        address rewardToken = message.destTokenAmounts[0].token;
        uint256 rewardAmount = message.destTokenAmounts[0].amount;
        lastReceivedTokenAddress = rewardToken;
        lastReceivedTokenAmount = rewardAmount;

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

    function testNotify(address rewardToken, uint256 rewardAmount) public {
        IERC20(rewardToken).transfer(streamer, rewardAmount);
        IChildChainStreamer(streamer).notify_reward_amount(rewardToken);
    }

    /* Admin */
    /// @notice Fallback function to allow the contract to receive Ether.
    /// @dev This function has no function body, making it a default function for receiving Ether.
    /// It is automatically called when Ether is transferred to the contract without any data.
    receive() external payable {}

    /// @dev Whitelists a chain for transactions.
    /// @notice This function can only be called by the owner.
    /// @param _sourceChainSelector The selector of the source chain to be whitelisted.
    function whitelistSourceChain(uint64 _sourceChainSelector) external onlyOwner {
        whitelistedSourceChains[_sourceChainSelector] = true;
    }

    /// @dev Denylists a chain for transactions.
    /// @notice This function can only be called by the owner.
    /// @param _sourceChainSelector The selector of the source chain to be denylisted.
    function denylistSourceChain(uint64 _sourceChainSelector) external onlyOwner {
        whitelistedSourceChains[_sourceChainSelector] = false;
    }

    /// @dev Whitelists a sender.
    /// @notice This function can only be called by the owner.
    /// @param _sender The address of the sender.
    function whitelistSender(address _sender) external onlyOwner {
        whitelistedSenders[_sender] = true;
    }

    /// @dev Denylists a sender.
    /// @notice This function can only be called by the owner.
    /// @param _sender The address of the sender.
    function denySender(address _sender) external onlyOwner {
        whitelistedSenders[_sender] = false;
    }

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
