// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

/// @title ChildChainRegistry
/// @dev A contract to register and manage gauge sets on the child chain.
/// Gauge sets consist of a root gauge, receiver, streamer, and child gauge addresses.
/// Only the owner or the designated factory can register and unregister gauge sets.
contract ChildChainRegistry is Ownable {
    event RegisterFactory(address indexed factory);
    event RegisterGaugeSet(
        address indexed rootGauge, address receiver, address streamer, address childGauge, uint256 timestamp
    );
    event EditGaugeSet(
        address indexed rootGauge, address receiver, address streamer, address childGauge, uint256 timestamp
    );
    event UnregisterGaugeSet(address indexed rootGauge, address receiver, address streamer, address childGauge);
    event RecalculateSubgraph();

    struct GaugeSet {
        address receiver;
        address streamer;
        address childGauge;
        uint256 updatedAt;
    }

    address public factory;
    uint256 public nActiveGauges;
    address[] public rootGaugeHistory;
    mapping(address => GaugeSet) public gaugeSets; //  Associate mainnet root gauge address with gauge sets.

    modifier onlyOwnerOrFactory() {
        require(msg.sender == owner() || msg.sender == factory, "Ownable: caller is not the owner or factory");
        _;
    }

    constructor() {}

    /// @dev Sets the secondary write-only address for registering new gauge sets from factory
    /// @param _factory The address of the factory contract.
    function setFactory(address _factory) public onlyOwner {
        factory = _factory;
        emit RegisterFactory(_factory);
    }

    /// @dev Registers a new gauge set with the specified addresses.
    /// @param rootGauge The mainnet address of the root gauge.
    /// @param receiver The address of the receiver contract.
    /// @param streamer The address of the streamer contract.
    /// @param childGauge The address of the child gauge.
    /// Emits a Registered event upon successful registration.
    function registerGaugeSet(address rootGauge, address receiver, address streamer, address childGauge)
        public
        onlyOwnerOrFactory
    {
        require(gaugeSets[rootGauge].childGauge == address(0), "gauge set for root gauge address already exists");

        rootGaugeHistory.push(rootGauge);
        gaugeSets[rootGauge] = GaugeSet(receiver, streamer, childGauge, block.timestamp);
        nActiveGauges++;
        emit RegisterGaugeSet(rootGauge, receiver, streamer, childGauge, block.timestamp);
    }

    /// @dev Updates an existing gauge set with new contract addresses.
    /// @param rootGauge The mainnet address of the root gauge.
    /// @param receiver The address of the receiver contract.
    /// @param streamer The address of the streamer contract.
    /// @param childGauge The address of the child gauge.
    function editGaugeSet(address rootGauge, address receiver, address streamer, address childGauge) public onlyOwner {
        gaugeSets[rootGauge] = GaugeSet(receiver, streamer, childGauge, block.timestamp);
        emit EditGaugeSet(rootGauge, receiver, streamer, childGauge, block.timestamp);
    }

    /// @dev Unregisters a gauge set associated with the specified root gauge address.
    /// @param rootGauge The mainnet address of the root gauge.
    /// Emits an Unregistered event upon successful unregistration.
    function unregisterGaugeSet(address rootGauge) public onlyOwner {
        require(gaugeSets[rootGauge].receiver != address(0), "Gauge set not found for root gauge address");
        GaugeSet memory set = gaugeSets[rootGauge];
        delete gaugeSets[rootGauge];
        nActiveGauges--;
        emit UnregisterGaugeSet(rootGauge, set.receiver, set.streamer, set.childGauge);
    }

    /// @dev Returns array of root gauges with registered child chain addresses
    function activeRootGauges() public view returns (address[] memory active) {
        uint256 j;
        active = new address[](nActiveGauges);
        for (uint256 i; i < rootGaugeHistory.length; i++) {
            address testAddr = rootGaugeHistory[i];
            if (gaugeSets[testAddr].childGauge != address(0)) {
                active[j] = testAddr;
                j++;
            }
        }
        return active;
    }

    /// @dev Emits an event to manually invoke the subgraph to recalculate data
    function poke() public onlyOwner {
        emit RecalculateSubgraph();
    }
}
