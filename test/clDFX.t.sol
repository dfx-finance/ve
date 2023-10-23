// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";
import {clDFX} from "../src/cldfx/clDFX.sol";

contract ClDfxTest is Test {
    clDFX public dfx;

    function setUp() public {
        dfx = new clDFX();
    }

    function test_Increment() public {
        // assertEq(2, 1);
    }
}
