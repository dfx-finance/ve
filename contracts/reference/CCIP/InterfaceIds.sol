// SPDX-License-Identifier: Unlicensed
pragma solidity ^0.8.0;

import "../../testing/IERC165.sol";
import "./IAny2EVMMessageReceiver.sol";

contract InterfaceIds {
    constructor() {}

    function getInterfaceIds() external pure returns (bytes4, bytes4) {
        return (type(IAny2EVMMessageReceiver).interfaceId, type(IERC165).interfaceId);
    }
}
