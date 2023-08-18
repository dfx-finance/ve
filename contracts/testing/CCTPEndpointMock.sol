// SPDX-License-Identifier: MIT
// Base on LzEndpointMock.sol
pragma solidity ^0.8.10;

import {LinkTokenInterface} from "@chainlink/contracts/src/v0.8/interfaces/LinkTokenInterface.sol";
// import {IERC20} from "@chainlink/contracts-ccip/src/v0.8/vendor/openzeppelin-solidity/v4.8.0/token/ERC20/IERC20.sol";
// import {IRouterClient} from "@chainlink/contracts-ccip/src/v0.8/ccip/interfaces/IRouterClient.sol";
// import {Client} from "@chainlink/contracts-ccip/src/v0.8/ccip/libraries/Client.sol";

contract CctpEndpointMock {
    // uint8 internal constant _NOT_ENTERED = 1;
    // uint8 internal constant _ENTERED = 2;

    mapping(address => address) public cctpEndpointLookup;

    uint16 public mockChainId;

    // // reentrancy guard
    // uint8 internal _send_entered_state = 1;
    // uint8 internal _receive_entered_state = 1;

    // modifier sendNonReentrant() {
    //     require(_send_entered_state == _NOT_ENTERED, "MockCCTP: no send reentrancy");
    //     _send_entered_state = _ENTERED;
    //     _;
    //     _send_entered_state = _NOT_ENTERED;
    // }

    // modifier receiveNonReentrant() {
    //     require(_receive_entered_state == _NOT_ENTERED, "MockCCTP: no receive reentrancy");
    //     _receive_entered_state = _ENTERED;
    //     _;
    //     _receive_entered_state = _NOT_ENTERED;
    // }

    constructor(uint16 _chainId) {
        mockChainId = _chainId;
    }

    // ------------------------------ CCTP Endpoint Functions ------------------------------
    function send(bytes memory _path) external payable {
        require(_path.length == 40, "LayerZeroMock: incorrect remote address size"); // only support evm chains

        address dstAddr;
        assembly {
            dstAddr := mload(add(_path, 20))
        }

        address cctpEndpoint = cctpEndpointLookup[dstAddr];
    }

    // ------------------------------ Other Public/External Functions --------------------------------------------------
    function setDestCctpEndpoint(address destAddr, address lzEndpointAddr) external {
        cctpEndpointLookup[destAddr] = lzEndpointAddr;
    }
}
