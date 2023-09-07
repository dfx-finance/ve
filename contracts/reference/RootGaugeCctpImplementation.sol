// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.10;

/**
 * @title Root-Chain Gauge CCTP Transfer
 * @author DFX Finance
 * @notice Receives total allocated weekly DFX emission mints and sends to L2 gauge
 */
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelinUpgradeable/contracts/access/AccessControlUpgradeable.sol";
import {LinkTokenInterface} from "@chainlink/contracts/src/v0.8/interfaces/LinkTokenInterface.sol";
import {Client} from "@chainlink/contracts-ccip/src/v0.8/ccip/libraries/Client.sol";
import {IRouterClient} from "@chainlink/contracts-ccip/src/v0.8/ccip/interfaces/IRouterClient.sol";

contract RootGaugeCctpImplementation is AccessControlUpgradeable {
    // Custom errors to provide more descriptive revert messages.
    error NotEnoughBalance(uint256 currentBalance, uint256 calculatedFees); // Used to make sure contract has enough balance to cover the fees.

    // Event emitted when a message is sent to another chain.
    // The unique ID of the CCIP message.
    // The chain selector of the destination chain.
    // The address of the receiver on the destination chain.
    // The token address that was transferred.
    // The token amount that was transferred.
    // the token address used to pay CCIP fees.
    // The fees paid for sending the CCIP message.
    event MessageSent(
        bytes32 indexed messageId,
        uint64 indexed destinationChainSelector,
        address receiver,
        address token,
        uint256 tokenAmount,
        address feeToken,
        uint256 fees
    );

    string public name;
    string public symbol;
    uint256 public period;
    uint256 public startEpochTime;
    uint256 constant WEEK = 604800;

    IRouterClient router;
    address public controller;
    address public distributor;
    uint64 public destinationChain;
    address public destination;
    address public DFX;
    address public feeToken;

    address public admin;

    constructor() initializer {}

    /// @dev Modifier that checks whether the msg.sender is admin
    modifier onlyAdmin() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    /// @dev Modifier that checks whether the msg.sender is the distributor contract address
    modifier onlyDistributor() {
        require(msg.sender == distributor, "Not distributor");
        _;
    }

    /// @notice Contract initializer
    /// @param _symbol Gauge base symbol
    /// @param _DFX Address of the DFX token
    /// @param _distributor Address of the mainnet rewards distributor
    /// @param _router Address of the CCIP message router
    /// @param _destinationChain Chain ID of the chain with the destination gauge. CCIP uses its own set of chain selectors to identify blockchains
    /// @param _destination Address of the destination gauge on the sidechain
    /// @param _admin Admin who can kill the gauge
    function initialize(
        string memory _symbol,
        address _DFX,
        address _distributor,
        address _router,
        uint64 _destinationChain,
        address _destination,
        address _feeToken,
        address _admin
    ) external initializer {
        require(_DFX != address(0), "Token cannot be zero address");

        name = string(abi.encodePacked("DFX ", _symbol, " Gauge"));
        symbol = string(abi.encodePacked(_symbol, "-gauge"));

        DFX = _DFX;
        distributor = _distributor;
        router = IRouterClient(_router);
        destinationChain = _destinationChain; // destination chain selector
        destination = _destination; // destination address on l2
        feeToken = _feeToken;
        admin = _admin;

        period = block.timestamp / WEEK - 1;
    }

    /* Parameters */
    function updateDestination(address _newDestination) external onlyAdmin {
        destination = _newDestination;
    }

    function updateDistributor(address _newDistributor) external onlyAdmin {
        distributor = _newDistributor;
    }

    /* Gauge actions */
    function testFee(uint256 _amount) external view returns (uint256) {
        Client.EVM2AnyMessage memory message = _buildCcipMessage(destination, DFX, _amount, feeToken);
        return router.getFee(destinationChain, message);
    }

    function _notifyReward(uint256 _amount) internal returns (bytes32) {
        startEpochTime = block.timestamp;

        // Max approve spending of rewards tokens by router
        if (IERC20(DFX).allowance(address(this), address(router)) < _amount) {
            IERC20(DFX).approve(address(router), type(uint256).max);
        }

        Client.EVM2AnyMessage memory message = _buildCcipMessage(destination, DFX, _amount, feeToken);
        uint256 fees = router.getFee(destinationChain, message);

        // When fee token is set, send messages across CCIP using token. Otherwise,
        // use the native gas token
        bytes32 messageId;
        if (feeToken != address(0)) {
            if (fees > IERC20(feeToken).balanceOf(address(this))) {
                revert NotEnoughBalance(IERC20(feeToken).balanceOf(address(this)), fees);
            }
            // Max approve spending of gas tokens by router
            if (IERC20(feeToken).allowance(address(this), address(router)) < fees) {
                IERC20(feeToken).approve(address(router), type(uint256).max);
            }
            //     messageId = router.ccipSend(destinationChain, message);
        } else {
            if (fees > address(this).balance) {
                revert NotEnoughBalance(address(this).balance, fees);
            }
            messageId = router.ccipSend{value: fees}(destinationChain, message);
        }

        // Emit an event with message details
        emit MessageSent(messageId, destinationChain, destination, DFX, _amount, feeToken, fees);
        return messageId;
    }

    // function notifyReward(uint256 _amount) external returns (bytes32) {
    //     bytes32 messageId = _notifyReward(_amount);
    //     return messageId;
    // }

    function notifyReward(address, uint256 _amount) external returns (bytes32) {
        bytes32 messageId = _notifyReward(_amount);
        return messageId;
    }

    /* CCIP */
    /// @notice Construct a CCIP message.
    /// @dev This function will create an EVM2AnyMessage struct with all the necessary information for tokens transfer.
    /// @param _receiver The address of the receiver.
    /// @param _token The token to be transferred.
    /// @param _amount The amount of the token to be transferred.
    /// @param _feeTokenAddress The address of the token used for fees. Set address(0) for native gas.
    /// @return Client.EVM2AnyMessage Returns an EVM2AnyMessage struct which contains information for sending a CCIP message.
    function _buildCcipMessage(address _receiver, address _token, uint256 _amount, address _feeTokenAddress)
        internal
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

    /// @notice Fallback function to allow the contract to receive Ether.
    /// @dev This function has no function body, making it a default function for receiving Ether.
    /// It is automatically called when Ether is transferred to the contract without any data.
    receive() external payable {}

    /* Admin */
    /// @notice Emergency withdraw
    /// @param _beneficiary Receiver of emergeny withdraw
    /// @param _token Address of token to withdraw
    /// @param _amount Amount to withdraw
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
