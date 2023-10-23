// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title CCIP Sender
 * @author DFX Finance
 * @notice Sends rewards to configured L2 destinations using Chainlink router
 */
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import {Client} from "@chainlink/contracts-ccip/src/v0.8/ccip/libraries/Client.sol";
import {IRouterClient} from "@chainlink/contracts-ccip/src/v0.8/ccip/interfaces/IRouterClient.sol";

contract CcipSender is Initializable {
    // Custom errors to provide more descriptive revert messages.
    error NotEnoughBalance(uint256 currentBalance, uint256 calculatedFees); // Used to make sure contract has enough balance to cover the fees.

    // The address of the DFX reward token
    address public immutable DFX;
    // Instance of CCIP Router
    IRouterClient router;
    // Chain selector for the destination blockchain (see Chainlink docs)
    uint64 public targetChainSelector;
    // The token used for paying fees in cross-chain interactions
    address public feeToken;
    // The default gas price for the _ccipReceive function on the L2
    uint256 public l2GasLimitFee = 200_000; // default gas price for _ccipReceive

    // The address with administrative privileges over this contract
    address public admin;

    // Destination chain addresses
    mapping(address => address) public destinations;

    /// @notice An event emitted when a message is sent to another chain.
    /// @param messageId The unique ID of the CCIP message.
    /// @param destinationChainSelector The chain selector of the destination chain.
    /// @param receiver The address of the receiver on the destination chain.
    /// @param token The token address that was transferred.
    /// @param tokenAmount The token amount that was transferred.
    /// @param feeToken The token address used to pay CCIP fees.
    /// @param fees The fees paid for sending the CCIP message.
    event MessageSent(
        bytes32 indexed messageId,
        uint64 indexed destinationChainSelector,
        address receiver,
        address token,
        uint256 tokenAmount,
        address feeToken,
        uint256 fees
    );

    /// @dev Modifier that checks whether the msg.sender is admin
    modifier onlyAdmin() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    /// @notice Contract constructor
    constructor(address _DFX) initializer {
        DFX = _DFX;
    }

    function initialize(address _router, uint64 _selector, address _feeToken, address _admin) public {
        router = IRouterClient(_router);
        targetChainSelector = _selector;
        feeToken = _feeToken;
        admin = _admin;

        // Max approve spending of rewards tokens by sender
        IERC20(DFX).approve(address(_router), type(uint256).max);
    }

    function relayReward(uint256 amount) public returns (bytes32) {
        IERC20(DFX).transferFrom(msg.sender, address(this), amount);

        address destination = destinations[msg.sender];

        Client.EVM2AnyMessage memory message = _buildCcipMessage(destination, DFX, amount, feeToken);
        uint256 fees = router.getFee(targetChainSelector, message);

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
            messageId = router.ccipSend(targetChainSelector, message);
        } else {
            if (fees > address(this).balance) {
                revert NotEnoughBalance(address(this).balance, fees);
            }
            messageId = router.ccipSend{value: fees}(targetChainSelector, message);
        }

        // Emit an event with message details
        emit MessageSent(messageId, targetChainSelector, destination, DFX, amount, feeToken, fees);
        return messageId;
    }

    /// @notice Fallback function to allow the contract to receive Ether.
    /// @dev This function has no function body, making it a default function for receiving Ether.
    /// It is automatically called when Ether is transferred to the contract without any data.
    receive() external payable {}

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
        view
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
                Client.EVMExtraArgsV1({gasLimit: l2GasLimitFee, strict: false})
                ),
            // Set the feeToken to a feeTokenAddress, indicating specific asset will be used for fees
            feeToken: _feeTokenAddress
        });
        return evm2AnyMessage;
    }

    /* Admin */
    function setSelector(uint64 selector) public onlyAdmin {
        targetChainSelector = selector;
    }

    /// @notice Set the token to use for CCIP message fees.
    /// @dev Only callable by the current admin.
    /// @param _newFeeToken Set a new fee token (LINK, wrapped native or a native token).
    function setFeeToken(address _newFeeToken) external onlyAdmin {
        feeToken = _newFeeToken;
    }

    /// @notice Set the maximum gas to be used by the _ccipReceive function override on L2.
    ///         Unused gas will not be refunded.
    /// @dev Only callable by the current admin.
    /// @param _newGasLimit Set a new L2 gas limit.
    function setL2GasLimit(uint256 _newGasLimit) external onlyAdmin {
        l2GasLimitFee = _newGasLimit;
    }

    function addL2Destination(address rootGauge, address receiver) public onlyAdmin {
        destinations[rootGauge] = receiver;
    }

    /// @notice Withdraw ERC20 tokens accidentally sent to the contract.
    /// @dev Only callable by the admin.
    /// @param _beneficiary Address to send the tokens to.
    /// @param _token Address of the token to withdraw.
    /// @param _amount Amount of the token to withdraw.
    function emergencyWithdraw(address _beneficiary, address _token, uint256 _amount) external onlyAdmin {
        IERC20(_token).transfer(_beneficiary, _amount);
    }

    /// @notice Withdraw native Ether accidentally sent to the contract.
    /// @dev Only callable by the admin.
    /// @param _beneficiary Address to send the Ether to.
    /// @param _amount Amount of Ether to withdraw.
    function emergencyWithdrawNative(address _beneficiary, uint256 _amount) external onlyAdmin {
        (bool sent,) = _beneficiary.call{value: _amount}("");
        require(sent, "Failed to send Ether");
    }
}
