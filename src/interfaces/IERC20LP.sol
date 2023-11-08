// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IERC20LP is IERC20 {
    function setMinter(address minter) external;
    function mint(address to, uint256 amount) external;
}
