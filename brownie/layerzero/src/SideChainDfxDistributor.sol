// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

import "./external/AccessControlUpgradeable.sol";
import "./interfaces/ISideChainGaugeTracker.sol";
import "./SideChainDfxDistributorEvents.sol";

contract SideChainDfxDistributor is SideChainDfxDistributorEvents, AccessControlUpgradeable {
    using SafeERC20 for IERC20;

    /// @notice Role for governors only
    bytes32 public constant GOVERNOR_ROLE = keccak256("GOVERNOR_ROLE");
    /// @notice Role for the guardian
    bytes32 public constant GUARDIAN_ROLE = keccak256("GUARDIAN_ROLE");

    /// @notice Length of a week in seconds
    uint256 public constant WEEK = 3600 * 24 * 7;

    /// @notice Reduction of the emission rate
    uint256 public constant RATE_REDUCTION_COEFFICIENT = 1007827884862117171; // 1.5 ^ (1/52) * 10**18

    /// @notice Time at which the emission rate is updated
    uint256 public constant RATE_REDUCTION_TIME = WEEK;

    /// @notice Base used for computation
    uint256 public constant BASE = 10 ** 18;

    /// @notice Maps the address of a gauge to the last time this gauge received rewards
    mapping(address => uint256) public lastTimeGaugePaid;

    /// @notice Maps the address of a gauge to whether it was killed or not
    /// A gauge killed in this contract cannot receive rewards
    mapping(address => bool) public killedGauges;

    /// @notice Address of the DFX token given as reward
    IERC20 public rewardToken;

    /// @notice Address of the `GaugeTracker` contract
    ISideChainGaugeTracker public gaugeTracker;

    /// @notice DFX current emission rate, it is first defined in the initializer and then updated every week
    uint256 public rate;

    /// @notice Timestamp at which the current emission epoch started
    uint256 public startEpochTime;

    /// @notice Amount of DFX tokens distributed through staking at the start of the epoch
    /// This is an informational variable used to track how much has been distributed through liquidity mining
    uint256 public startEpochSupply;

    /// @notice Index of the current emission epoch
    uint256 public miningEpoch;

    /// @notice Whether DFX distribution through this contract is on or no
    bool public distributionsOn;

    function initialize(address _rewardToken, address _tracker, address governor, address guardian)
        external
        initializer
    {
        require(
            _rewardToken != address(0) && _tracker != address(0) && governor != address(0) && guardian != address(0),
            "0"
        );
        rewardToken = IERC20(_rewardToken);
        gaugeTracker = ISideChainGaugeTracker(_tracker);
        miningEpoch = 0;
        distributionsOn = false;
        _setRoleAdmin(GOVERNOR_ROLE, GOVERNOR_ROLE);
        _setRoleAdmin(GUARDIAN_ROLE, GOVERNOR_ROLE);
        _setupRole(GUARDIAN_ROLE, guardian);
        _setupRole(GOVERNOR_ROLE, governor);
        _setupRole(GUARDIAN_ROLE, governor);
    }

    constructor() initializer {}

    // ======================== Internal Functions =================================
    /// @notice Updates mining rate and supply at the start of the epoch
    /// @dev Any modifying mining call must also call this
    /// @dev It is possible that more than one week past between two calls of this function, and for this reason
    /// this function has been slightly modified from Curve implementation by Angle Core Team
    function _updateMiningParameters() internal {
        // When entering this function, we always have: `(block.timestamp - startEpochTime) / RATE_REDUCTION_TIME >= 1`
        uint256 epochDelta = (block.timestamp - startEpochTime) / RATE_REDUCTION_TIME;

        // Storing intermediate values for the rate and for the `startEpochSupply`
        uint256 _rate = rate;
        uint256 _startEpochSupply = startEpochSupply;

        startEpochTime += RATE_REDUCTION_TIME * epochDelta;
        miningEpoch += epochDelta;

        for (uint256 i = 0; i < epochDelta; i++) {
            // Updating the intermediate values of the `startEpochSupply`
            _startEpochSupply += _rate * RATE_REDUCTION_TIME;
            _rate = (_rate * BASE) / RATE_REDUCTION_COEFFICIENT;
        }
        rate = _rate;
        startEpochSupply = _startEpochSupply;
        emit UpdateMiningParameters(block.timestamp, _rate, _startEpochSupply);
    }

    /// @notice Internal function to distribute rewards to a gauge
    /// @param gaugeAddr Address of the gauge to distribute rewards to
    /// @return weeksElapsed Weeks elapsed since the last call
    /// @return rewardTally Amount of rewards distributed to the gauge
    /// @dev The reason for having an internal function is that it's called by the `distributeReward` and the
    /// `distributeRewardToMultipleGauges`
    /// @dev Although they would need to be performed all the time this function is called, this function does not
    /// contain checks on whether distribution is on, and on whether rate should be reduced. These are done in each external
    /// function calling this function for gas efficiency
    function _distributeReward(address gaugeAddr) internal returns (uint256 weeksElapsed, uint256 rewardTally) {
        // Checking if the gauge has been added or if it still possible to distribute rewards to this gauge
        int128 gaugeType = ISideChainGaugeTracker(gaugeTracker).gaugeTypes(gaugeAddr);
        require(gaugeType >= 0 && !killedGauges[gaugeAddr], "110");

        // Calculate the elapsed time in weeks
        uint256 lastTimePaid = lastTimeGaugePaid[gaugeAddr];

        // Edge case for first reward of this gauge
        if (lastTimePaid == 0) {
            weeksElapsed = 1;
            if (gaugeType == 0) {
                // We give full approval for the gauges with type zero which correspond to the staking
                // contracts of the protocol
                rewardToken.safeApprove(gaugeAddr, type(uint256).max);
            } else {
                // Truncation desired
                weeksElapsed = (block.timestamp - lastTimePaid) / WEEK;
                // Return early here for 0 weeks instead of throwing, as it could have bad effects in other contracts
                if (weeksElapsed == 0) {
                    return (0, 0);
                }
            }
        }
        rewardTally = 0;
        // We use this variable to keep track of the emission rate across different weeks
        uint256 weeklyRate = rate;
        for (uint256 i = 0; i < weeksElapsed; i++) {
            uint256 relWeightAtWeek = gaugeTracker.gaugeRelativeWeight(gaugeAddr, block.timestamp - WEEK * i);
            // if (i == 0) {
            //     // Mutative, for the current week: makes sure the weight is checkpointed.
            // }
            ILiquidityGauge(gaugeAddr).deposit_reward_token(address(rewardToken), rewardTally);
        }

        emit RewardDistributed(gaugeAddr, rewardTally);
    }

    // ======================== Public Functions =================================
    function distributeReward(address gaugeAddr) public {
        // Checking if the gauge has been added or if it is still possible to distribute rewards to this gauge
        int128 gaugeType = ISideChainGaugeTracker(gaugeTracker).gaugeTypes(gaugeAddr);
        require(gaugeType >= 0 && !killedGauges[gaugeAddr], "110");

        // Checking if distribution is on
        require(distributionsOn == true, "109");
        // Updating rate distribution parameters if need be
        if (block.timestamp >= startEpochTime + RATE_REDUCTION_TIME) {
            _updateMiningParameters();
        }
    }

    // ======================== Governor Functions =================================
    /// @notice Toggles the status of a gauge to either killed or unkilled
    /// @param gaugeAddr Gauge to toggle the status of
    /// @dev It is impossible to kill a gauge in the `GaugeController` contract, for this reason killing of gauges
    /// takes place in the `DfxDistributor` contract
    /// @dev This means that people could vote for a gauge in the gauge controller contract but that rewards are not going
    /// to be distributed to it in the end: people would need to remove their weights on the gauge killed to end the diminution
    /// in rewards
    /// @dev In the case of a gauge being killed, this function resets the timestamps at which this gauge has been approved and
    /// disapproves the gauge to spend the token
    /// @dev It should be cautiously called by governance as it could result in less DFX overall rewards than initially planned
    /// if people do not remove their voting weights to the killed gauge
    function toggleGauge(address gaugeAddr) external onlyRole(GOVERNOR_ROLE) {
        bool gaugeKilledMem = killedGauges[gaugeAddr];
        if (!gaugeKilledMem) {
            delete lastTimeGaugePaid[gaugeAddr];
            rewardToken.safeApprove(gaugeAddr, 0);
        }
        killedGauges[gaugeAddr] = !gaugeKilledMem;
        emit GaugeToggled(gaugeAddr, !gaugeKilledMem);
    }
}
