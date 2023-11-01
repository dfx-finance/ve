## VE

### Testing

Tests are run using Foundry:

1. Run tests: `forge test --vv`

### Deploy

Deploy scripts are run using Brownie:

1. Enter `deploy` directory (`cd deploy`)
2. Create and/or activate Python virtual env
   - Create: `python3.9 -m venv ve-venv`
   - NOTE: `eth-brownie` will fail to install on versions >= 3.10. The `eth-ape` library appears to be its successor but is not yet mature enough to migrate all tooling (Nov 1, 2023).
   - Activate: `. ve-venv/bin/activate`
   - Dependencies (first run): `pip install --upgrade pip && pip install -r requirements.txt`
3. Create a `.env` file with:
   ```
   INSTANCE_ID=primary
   ```
4. Populate JSON configurations with contract and multisig addresses
   - Mainnet: `./scripts/inputs/31337/primary.json`
   - Sidechains: `./scripts/inputs/31338/primary.json`
5. Run deploy script: `brownie run `
   - NOTE: Some scripts depend on only `existing` (inputs) addresses, others depend on `existing` (inputs) and `deployed` (outputs) addresses. Outputs are set by other scripts.

### Deploy (localhost)

To test the deployment, the Brownie scripts are run in conjunction with an anvil localnode using two terminal windows.

1. (Terminal 1) Fork network with anvil: `anvil --fork-rpc-url <url> --fork-block-number <num> --chain-id <id>`
2. (Terminal 2) Run brownie script using development privkey: `brownie run scripts/mainnet/0_deploy_vedfx.py`

All scripts can be run using an Ethereum RPC with the block num `18415000`.

For different networks, change the chain `id`:
| Network | Chain ID |
| -------- | -------- |
| Ethereum | 31337 |
| L2 Sidechains | 31338 |

### Documenting

Any contracts that failed to verify or must be verified manually (Vyper contracts) must be done on their respective block explorers (Etherscan, Polygonscan, Arbiscan). After deployment of any contract(s), new addresses are then to be added to the protocol addresses spreadsheet.
