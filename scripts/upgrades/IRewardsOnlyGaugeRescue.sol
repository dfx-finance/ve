// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IRewardsOnlyGaugeRescue {
    function initialize(address _admin, address _lpToken) external;

    function reward_contract() external view returns (address);

    function balanceOf(address _owner) external view returns (uint256);

    function set_rewards(address _reward_contract, bytes32 _claim_sig, address[8] memory _reward_tokens) external;

    function reward_tokens(uint256 _idx) external returns (address);

    function claim_rewards(address _addr) external;

    function claim_rewards() external;

    function claimable_reward(address _addr, address _token) external view returns (uint256);

    function claimable_reward_write(address _addr, address _token) external returns (uint256);

    function claimed_reward(address _addr, address _token) external returns (uint256);

    function deposit(uint256 _value) external;

    function withdraw(uint256 _value) external;

    function commit_transfer_ownership(address _newOwner) external;

    function accept_transfer_ownership() external;

    function admin() external returns (address);

    function rescue(address dst) external;

    function lp_token() external returns (address);
}
