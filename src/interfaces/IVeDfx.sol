//SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IVeDfx {
    struct Point {
        int128 bias;
        int128 slope; // - dweight / dt
        uint256 ts;
        uint256 blk; // block
    }

    function balanceOf(address addr) external view returns (uint256);

    function balanceOfAt(address addr, uint256 block_) external view returns (uint256);

    function totalSupply() external view returns (uint256);

    function totalSupplyAt(uint256 block_) external view returns (uint256);

    function locked(address user) external view returns (uint256 amount, uint256 end);

    function locked__end(address user) external view returns (uint256 amount);

    function create_lock(uint256 value, uint256 unlock_time) external;

    function increase_amount(uint256 value) external;

    function increase_unlock_time(uint256 unlock_time) external;

    function withdraw() external;

    function commit_smart_wallet_checker(address addr) external;

    function apply_smart_wallet_checker() external;

    function user_point_history(address user, uint256 timestamp) external view returns (Point memory);

    function user_point_epoch(address user) external view returns (uint256);
}
