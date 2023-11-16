// SPDX-License-Identifier: MIT
// vyper -f bytecode --evm-version istanbul ChildChainStreamer.vy > streamer_bytecode.txt
pragma solidity ^0.8.19;

import "../DfxUpgradeableProxy.sol";
import "../interfaces/IRewardsOnlyGauge.sol";
import "../interfaces/IChildChainStreamer.sol";
import "./ChildChainReceiver.sol";

contract ChildChainFactory {
    event Deployed(
        address rootGauge, address router, address receiver, address streamer, address childGauge, address owner
    );
    event Registered(address rootGauge, address receiver, address streamer, address childGauge);
    event Unregistered(address rootGauge, address receiver, address streamer, address childGauge);
    event NewStreamerBytecode(string vyperVersion, string evmVersion, address deployer, uint256 timestamp);

    bytes public streamerBytecode;

    struct GaugeSet {
        address rootGauge;
        address receiver;
        address sender;
    }

    mapping(address => GaugeSet) public gaugeSets;

    address public owner;

    /// @dev Modifier that checks whether the msg.sender is owner
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    /// @notice Constructor initializes the factory contract.
    /// @param _owner The address of the contract owner.
    constructor(address _owner, bytes memory _streamerBytecode) {
        owner = _owner;
        streamerBytecode = _streamerBytecode;
    }

    /// @notice Constructor initializes the factory contract.
    /// @param vyperVersion The bytecode's Vyper compiler version.
    /// @param evmVersion The bytecode's EVM version.
    /// @param bytecode Contract's hexadecimal bytecode.
    function setStreamerBytecode(string memory vyperVersion, string memory evmVersion, bytes memory bytecode)
        public
        onlyOwner
    {
        streamerBytecode = bytecode;

        emit NewStreamerBytecode(vyperVersion, evmVersion, msg.sender, block.timestamp);
    }

    function _deployVyperContract(bytes memory bytecode, bytes memory params) public returns (address) {
        bytes memory bytecodeWithArgs = abi.encodePacked(bytecode, params);

        address newContract;
        assembly {
            mstore(0x0, bytecodeWithArgs)
            newContract := create(0, add(bytecodeWithArgs, 0x20), mload(bytecodeWithArgs))
        }
        require(newContract != address(0), "deployed failed");
        return newContract;
    }

    /// @notice Deploys and configures all contracts comprising a sidechain gauge
    /// @param rootGauge The mainnet address of the placeholder RootGauge
    /// @param ccipRouter The CCIP router address for the sidechain
    /// @param childGaugeImplementation Implementation address for gauge proxy
    /// @param lpt Address of gauge staking token
    /// @param deployedOwner Address of contracts owner
    /// @param deployedProxyOwner Address of proxy admin
    /// @param rewardToken Default token (DFX) provided as gauge reward
    function deployGaugeSet(
        address rootGauge,
        address ccipRouter,
        address childGaugeImplementation,
        address lpt,
        address deployedOwner,
        address deployedProxyOwner,
        address rewardToken
    ) public onlyOwner returns (address receiver, address streamer, address gauge) {
        // Deploy RewardsOnlyGauge contract
        bytes memory gaugeParams = abi.encodeWithSelector(IRewardsOnlyGauge.initialize.selector, address(this), lpt);
        DfxUpgradeableProxy _gauge = new DfxUpgradeableProxy(childGaugeImplementation, deployedProxyOwner, gaugeParams);
        gauge = address(_gauge);

        // Deploy ChildChainStreamer contract
        streamer = _deployVyperContract(streamerBytecode, abi.encode(address(this), gauge, rewardToken));

        // Deploy ChildChainReceiver contract
        ChildChainReceiver _receiver = new ChildChainReceiver(ccipRouter, streamer, deployedOwner);
        receiver = address(_receiver);

        // Configure contracts
        IChildChainStreamer(streamer).set_reward_distributor(rewardToken, gauge);
        address[8] memory rewards =
            [rewardToken, address(0), address(0), address(0), address(0), address(0), address(0), address(0)];
        IRewardsOnlyGauge(gauge).set_rewards(streamer, IChildChainStreamer.get_reward.selector, rewards);

        IChildChainStreamer(streamer).commit_transfer_ownership(deployedOwner);
        IRewardsOnlyGauge(gauge).commit_transfer_ownership(deployedOwner);

        // Track gauge sets in registry
        gaugeSets[gauge] = GaugeSet(rootGauge, receiver, streamer);

        emit Deployed(rootGauge, ccipRouter, receiver, streamer, gauge, deployedOwner);
        emit Registered(rootGauge, receiver, streamer, gauge);
    }

    /**
     * Manual registration events for existing gauges  to enable tracking by subgraph
     */
    /// @notice Emit event for registering gauge sets not deployed by factory
    function registerGaugeSet(address rootGauge, address receiver, address streamer, address childGauge)
        public
        onlyOwner
    {
        gaugeSets[childGauge] = GaugeSet(rootGauge, receiver, streamer);
        emit Registered(rootGauge, receiver, streamer, childGauge);
    }

    /// @notice Emit event for de-registering gauge sets
    function unregisterGaugeSet(address rootGauge, address receiver, address streamer, address childGauge)
        public
        onlyOwner
    {
        delete gaugeSets[childGauge];
        emit Unregistered(rootGauge, receiver, streamer, childGauge);
    }

    /**
     * Admin functions
     */
    function setOwner(address newOwner) public onlyOwner {
        owner = newOwner;
    }
}
