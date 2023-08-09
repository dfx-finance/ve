//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract DFX_ is ERC20 {
    constructor(uint256 _initialSupply) ERC20("DFX", "DFX") {
        _mint(msg.sender, _initialSupply);
    }

    function mint(address to, uint256 amount) public {
        _mint(to, amount);
    }
}
