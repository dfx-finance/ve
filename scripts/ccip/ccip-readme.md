# CCIP L2 Gauges

## Overview

The L2 gauges flow comprises:

- `RootGaugeCcip.sol` (L1) - Placeholder gauge contract on L1 that receives rewards from mainnet distributor based on their voted weight. This contract then relays the rewards to a gauge on L2 using CCIP.
- `ChildChainReceiver.sol` (L2) - Receives messages and tokens from CCIP and forwards tokens to the ChildChainStreamer. This contract is responsible for calling the `notify_reward_amount()` function.
- `ChildChainStramer.vy` (L2) - Acts as a distributor for an RewardsOnlyGauge. This contract receives weekly rewards and linearly allocates rewards to gauges over a week.
- `RewardsOnlyGauge.vy` (L2) - Allows users to stake LPTs on L2 and receive rewards. Rewards are distributed without boost and functions similar to a standard StakingRewards contract.

## Deployment scripts

1. Deploy L2 contracts: `brownie run scripts/ccip/1_deploy_child_chain_gauge.py --network polygon-test`
2. Configure L1 deploy script (`./scripts/ccip/2_deploy_child_chain_gauge.py`) with L2 addresses
3. Deploy L1 contracts: `brownie run scripts/ccip/2_deploy_child_chain_gauge.py --network polygon-test`

- `deploy.py` - Upgrade live proxy with new implementation contract

## Live testing

- `migrate.py` - Migrate ccDFX and ETH from a deprecated Root Gauge (L1) to a new one
- `verify.py` - Verify an already-deployed Solidity contract on Etherscan (Polygonscan, etc.) with Browie. Configure API keys in repo .env

### L2 End-to-end

<!-- To manually call the L2 stack end-to-end -->

Test notify tx: https://mumbai.polygonscan.com/tx/0x13feb65de73918812dbcd31039edba71cfa4f2929c32fc3e515d5d6d28f463d0
Gas used: 0.00029946810401349 MATIC or 299468.10401349 Gwei
