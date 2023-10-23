// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IChildChainStreamer {
    function notify_reward_amount(address _token) external;
}
