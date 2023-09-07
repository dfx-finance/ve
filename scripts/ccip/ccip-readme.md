# CCIP L2 Gauges

## Deployment scripts

1. Deploy L2 contracts: `brownie run scripts/ccip/1_deploy_child_chain_gauge.py --network polygon-test`
2. Configure L1 deploy script (`./scripts/ccip/2_deploy_child_chain_gauge.py`) with L2 addresses
3. Deploy L1 contracts: `brownie run scripts/ccip/2_deploy_child_chain_gauge.py --network polygon-test`

- `deploy.py` - Upgrade live proxy with new implementation contract

## Live testing

- `migrate.py` - Migrate ccDFX and ETH from a deprecated Root Gauge (L1) to a new one
- `verify.py` - Verify an already-deployed Solidity contract on Etherscan (Polygonscan, etc.) with Browie. Configure API keys in repo .env
