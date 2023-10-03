# CCIP L2 Gauges

## Overview

The L2 gauges flow comprises:

- `RootGaugeCcip.sol` (L1) - Placeholder gauge contract on L1 that receives rewards from mainnet distributor based on their voted weight. This contract then relays the rewards to a gauge on L2 using CCIP.
- `ChildChainReceiver.sol` (L2) - Receives messages and tokens from CCIP and forwards tokens to the ChildChainStreamer. This contract is responsible for calling the `notify_reward_amount()` function.
- `ChildChainStramer.vy` (L2) - Acts as a distributor for an RewardsOnlyGauge. This contract receives weekly rewards and linearly allocates rewards to gauges over a week.
- `RewardsOnlyGauge.vy` (L2) - Allows users to stake LPTs on L2 and receive rewards. Rewards are distributed without boost and functions similar to a standard StakingRewards contract.

### Brownie notes

Brownie's `networks-config.yml` should contain an entry for `sepolia` and `polygon-test` for compatibility with this repo.

## Helpers

- `migrate.py` - Migrate ccDFX and ETH from a deprecated Root Gauge (L1) to a new one
- `upgrade.py` - Upgrade live proxy with new implementation contract
- `verify.py` - Verify an already-deployed Solidity contract on Etherscan (Polygonscan, etc.) with Browie. Configure API keys in repo .env

## L2 End-to-end

### Deployment scripts

1. Deploy L2 contracts: `brownie run scripts/ccip/layer2/1_deploy_child_chain_gauge.py --network polygon-test`
   - To check config: `brownie run scripts/ccip/layer2/check_setup.py --network polygon-test`
   - NOTE: Update `./utils/contstants_addresses.py` with newly deployed receiver, streamer and gauge (proxy) address
2. Configure L1 deploy script (`./scripts/ccip/2_deploy_child_chain_gauge.py`) with L2 addresses
3. Deploy L1 contracts: `brownie run scripts/ccip/mainnet/1_deploy_root_gauge.py --network sepolia`
   - To check config: `brownie run scripts/ccip/mainnet/check_setup.py --network sepolia`
   - NOTE: Update `./utils/contstants_addresses.py` with newly deployed root gauge address
4. Update L2 ChildChainReceiver with L1 RootGaugeCcip address: `brownie run scripts/ccip/layer2/2_set_sender.py --network polygon-test`

### Running

1. Fund the RootGaugeCcip with ETH for gas when calling `ccipSend()`.
2. To emulate the DfxDistributor, provide the RootGaugeCcip contract with rewards.
3. Then, call `notifyReward(_amount)` on RootGaugeCcip with the amount of rewards funded in step 2.
