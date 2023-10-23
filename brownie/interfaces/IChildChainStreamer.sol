// SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.8.19;

interface IChildChainStreamer {
    function notify_reward_amount(address _token) external;
}
