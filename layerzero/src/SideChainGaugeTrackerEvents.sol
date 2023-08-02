// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract SideChainGaugeTrackerEvents {
    event DistributionsToggled(bool _distributionsOn);
    event GaugeToggled(address indexed gaugeAddr, bool newStatus);
    event Recovered(address indexed tokenAddr, address indexed to, uint256 amount);
    event RewardDistributed(address indexed gaugeAddr, uint256 rewardTally);
}
