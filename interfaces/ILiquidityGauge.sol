// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.7;

interface ILiquidityGauge {
    function balanceOf(address _addr) external view returns (uint256 amount);

    function totalSupply() external view returns (uint256 amount);

    // solhint-disable-next-line
    function staking_token() external view returns (address stakingToken);

    // solhint-disable-next-line
    function deposit_reward_token(address _rewardToken, uint256 _amount) external;

    function deposit(
        uint256 _value,
        address _addr,
        // solhint-disable-next-line
        bool _claim_rewards
    ) external;

    // solhint-disable-next-line
    function claim_rewards(address _addr) external;

    // solhint-disable-next-line
    function claim_rewards(address _addr, address _receiver) external;
}
