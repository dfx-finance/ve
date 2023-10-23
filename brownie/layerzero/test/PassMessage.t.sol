// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
pragma abicoder v2;

import "forge-std/Test.sol";
import "../src/mocks/LZEndpointMock.sol";
import "../src/RootChainMessenger.sol";
import "../src/SideChainReceiver.sol";

contract PassMessage is Test {
    uint16 _chainId = 123;
    LZEndpointMock _lzEndpointMock;
    RootRewardsMessenger _messenger;
    SideChainReceiver _receiver;

    function setUp() public {
        // create a LayerZero mock endpoint for testing
        _lzEndpointMock = new LZEndpointMock(_chainId);

        _messenger = new RootRewardsMessenger(address(_lzEndpointMock));
        _receiver = new SideChainReceiver(address(_lzEndpointMock));

        _lzEndpointMock.setDestLzEndpoint(address(_messenger), address(_lzEndpointMock));
        _lzEndpointMock.setDestLzEndpoint(address(_receiver), address(_lzEndpointMock));

        _messenger.setTrustedRemote(_chainId, abi.encodePacked(address(_receiver), address(_messenger)));
        _receiver.setTrustedRemote(_chainId, abi.encodePacked(address(_messenger), address(_receiver)));
    }

    // Get required fee to send increment tx to layerzero
    function getFee(bytes memory payload) public view returns (uint256) {
        uint16 version = 1;
        uint256 baseValue = 200000;
        bytes memory adapterParams = abi.encodePacked(version, baseValue);
        (uint256 nativeFee,) = _messenger.estimateFee(_chainId, false, adapterParams, payload);
        return nativeFee;
    }

    function test_ArrayMessage() public {
        uint16 numGauges = 4;

        // Create dynamic array for gauge votes and assign values
        uint16[] memory voteData = new uint16[](numGauges);
        voteData[0] = 0;
        voteData[1] = 350;
        voteData[2] = 2000;
        voteData[3] = 500;

        // Prepare message
        bytes memory encodedVoteData = abi.encode(voteData);
        bytes memory encodedData = abi.encode(block.timestamp, numGauges, encodedVoteData);

        // Send across LayerZero
        uint256 nativeFee = getFee(encodedData);
        _messenger.sendGaugeRewardsProportions{value: nativeFee}(_chainId, encodedData);

        uint16 testGauge = 4;
        console.log("Total gauges: %s", _receiver.nGauges());
        console.log("Gauge (%s) votes: %s", testGauge, _receiver.voteData(testGauge - 1));
        console.log("Distributed at: %s", _receiver.distributedAt());
    }

    function test_SendGaugeWeights() public {
        // for (uint256 i = 0; i < gauges.length; i++) {
        //     _distributeReward(gauges[i]);
        // }

        // send
    }
}
