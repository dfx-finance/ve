## VE Deploy

Due to mixed Solity/Vyper contracts, a minimal `eth-brownie` configuration is used exclusively for chain and forked chain deployments.

### Getting Started

1. Create a `.env` file in `./deploy` dir with:

   ```
   INSTANCE_ID=primary
   ```

2. Populate JSON configurations with contract and multisig addresses
   - Mainnet: `./scripts/inputs/31337/primary.json`
   - Sidechains: `./scripts/inputs/31338/primary.json`
3. Run `anvil` node
   - Mainnet: `anvil --fork-url https://eth-mainnet.g.alchemy.com/v2/dRYOSLDw-_H1uT1bUtFKXipGKvKB1IX1 --fork-block-number 18415000 --chain-id 31337`
   - Sidechains: `anvil --fork-url https://eth-mainnet.g.alchemy.com/v2/dRYOSLDw-_H1uT1bUtFKXipGKvKB1IX1 --fork-block-number 18415000 --chain-id 31338`
4. Use `brownie run scripts/<chain>/<script>.py` to run deployment scripts.
   - NOTE: Some scripts depend on only `existing` (inputs) addresses, others depend on `existing` (inputs) and `deployed` (outputs) addresses. Outputs are set by other scripts.

#### References

- `dss-test`: JSON configurations
- `sparklend`: Deployment script layouts
