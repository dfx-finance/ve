// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IRewardsOnlyGauge {
    function initialize(address admin, address lpToken) external;

    function reward_contract() external view returns (address);

    function balanceOf(address _owner) external view returns (uint256);

    function set_rewards(address _reward_contract, bytes32 _claim_sig, address[8] memory _reward_tokens) external;

    function reward_tokens(uint256 idx) external returns (address);

    function claim_rewards(address user) external;

    function claimable_reward(address _addr, address _token) external view returns (uint256);

    function claimable_reward_write(address _addr, address _token) external returns (uint256);

    function deposit(uint256 _value) external;

    function withdraw(uint256 _value) external;
}
