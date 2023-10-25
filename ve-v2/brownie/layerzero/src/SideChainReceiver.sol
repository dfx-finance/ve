// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./lzApp/NonblockingLzApp.sol";

contract SideChainReceiver is NonblockingLzApp {
    uint256 public distributedAt;
    uint256 public nGauges;
    uint16[] public voteData;

    constructor(address _lzEndpoint) NonblockingLzApp(_lzEndpoint) {}

    function _nonblockingLzReceive(uint16, bytes memory, uint64, bytes memory payload) internal override {
        (uint256 timestamp, uint256 numGauges, bytes memory encodedVoteData) =
            abi.decode(payload, (uint256, uint256, bytes));

        distributedAt = timestamp;
        nGauges = numGauges;
        voteData = abi.decode(encodedVoteData, (uint16[]));
    }

    function setOracle(uint16 dstChainId, address oracle) external onlyOwner {
        // solhint-disable var-name-mixedcase
        uint256 TYPE_ORACLE = 6;
        // set the Oracle
        lzEndpoint.setConfig(lzEndpoint.getSendVersion(address(this)), dstChainId, TYPE_ORACLE, abi.encode(oracle));
    }

    function getOracle(uint16 remoteChainId) external view returns (address _oracle) {
        bytes memory bytesOracle =
            lzEndpoint.getConfig(lzEndpoint.getSendVersion(address(this)), remoteChainId, address(this), 6);
        assembly {
            _oracle := mload(add(bytesOracle, 32))
        }
    }
}
