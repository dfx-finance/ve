// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.19;

/// @title IDfxUpgradeableProxy
/// @notice Interface for the DFX upgradeable proxy contract
interface IDfxUpgradeableProxy {
    function getAdmin() external view returns (address _addr);

    function implementation() external view returns (address _implementation);

    function changeAdmin(address _addr) external;

    function upgradeTo(address _newImplementation) external;

    function upgradeToAndCall(address _newImplementation, bytes calldata data) external payable;
}
