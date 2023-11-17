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

    struct GaugeSetInfo {
        address rootGauge;
        address ccipRouter;
        address ccipSender;
        uint64 sourceChainSelector;
        address childGaugeImplementation;
        address lpt;
        address deployedOwner;
        address deployedProxyOwner;
        address rewardToken;
    }

    struct GaugeSet {
        address receiver;
        address sender;
        address childGauge;
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

    function _deployGaugeSet(GaugeSetInfo memory info)
        internal
        returns (address receiver, address streamer, address gauge)
    {
        // Deploy RewardsOnlyGauge contract
        bytes memory gaugeParams =
            abi.encodeWithSelector(IRewardsOnlyGauge.initialize.selector, address(this), info.lpt);
        DfxUpgradeableProxy _gauge =
            new DfxUpgradeableProxy(info.childGaugeImplementation, info.deployedProxyOwner, gaugeParams);
        gauge = address(_gauge);

        // Deploy ChildChainStreamer contract
        streamer = _deployVyperContract(streamerBytecode, abi.encode(address(this), gauge, info.rewardToken));

        // Deploy ChildChainReceiver contract
        ChildChainReceiver _receiver = new ChildChainReceiver(info.ccipRouter, streamer, address(this));
        receiver = address(_receiver);

        // Configure contracts
        _receiver.whitelistSender(info.ccipSender);
        _receiver.whitelistSourceChain(info.sourceChainSelector);
        IChildChainStreamer(streamer).set_reward_distributor(info.rewardToken, receiver);
        address[8] memory rewards =
            [info.rewardToken, address(0), address(0), address(0), address(0), address(0), address(0), address(0)];
        IRewardsOnlyGauge(gauge).set_rewards(streamer, IChildChainStreamer.get_reward.selector, rewards);

        _receiver.setOwner(info.deployedOwner);
        IChildChainStreamer(streamer).commit_transfer_ownership(info.deployedOwner);
        IRewardsOnlyGauge(gauge).commit_transfer_ownership(info.deployedOwner);

        // Track gauge sets in registry
        gaugeSets[info.rootGauge] = GaugeSet(receiver, streamer, gauge);

        emit Deployed(info.rootGauge, info.ccipRouter, receiver, streamer, gauge, info.deployedOwner);
        emit Registered(info.rootGauge, receiver, streamer, gauge);

        return (receiver, streamer, gauge);
    }

    /// @notice Deploys and configures all contracts comprising a sidechain gauge
    /// @param rootGauge The mainnet address of the placeholder RootGauge
    /// @param ccipRouter The CCIP router address for the sidechain
    /// @param ccipRouter The mainnet address of the CCIP sender contract to whitelist
    /// @param childGaugeImplementation Implementation address for gauge proxy
    /// @param lpt Address of gauge staking token
    /// @param deployedOwner Address of contracts owner
    /// @param deployedProxyOwner Address of proxy admin
    /// @param rewardToken Default token (DFX) provided as gauge reward
    function deployGaugeSet(
        address rootGauge,
        address ccipRouter,
        address ccipSender,
        uint64 sourceChainSelector,
        address childGaugeImplementation,
        address lpt,
        address deployedOwner,
        address deployedProxyOwner,
        address rewardToken
    ) external onlyOwner returns (address receiver, address streamer, address gauge) {
        GaugeSetInfo memory setInfo = GaugeSetInfo(
            rootGauge,
            ccipRouter,
            ccipSender,
            sourceChainSelector,
            childGaugeImplementation,
            lpt,
            deployedOwner,
            deployedProxyOwner,
            rewardToken
        );
        return _deployGaugeSet(setInfo);
    }

    /**
     * Manual registration events for existing gauges  to enable tracking by subgraph
     */
    /// @notice Emit event for registering gauge sets not deployed by factory
    function registerGaugeSet(address rootGauge, address receiver, address streamer, address childGauge)
        public
        onlyOwner
    {
        gaugeSets[rootGauge] = GaugeSet(receiver, streamer, childGauge);
        emit Registered(rootGauge, receiver, streamer, childGauge);
    }

    /// @notice Emit event for de-registering gauge sets
    function unregisterGaugeSet(address rootGauge, address receiver, address streamer, address childGauge)
        public
        onlyOwner
    {
        delete gaugeSets[rootGauge];
        emit Unregistered(rootGauge, receiver, streamer, childGauge);
    }

    /**
     * Admin functions
     */
    function setOwner(address newOwner) public onlyOwner {
        owner = newOwner;
    }
}
