## VE

### Configuration

- To keep packages isolated between `forge` and `eth-brownie`, there should be **TWO** Python virtual envs to manage. In most cases, they will be worked on in isolation, but this is something to be careful of. TBD if it is better to unify these into the root virtual env.

### Testing

Tests are run using Foundry:

1. Run tests: `forge test --ffi -vv`

### Deploy

Deploy scripts are run using Brownie:

1. Replace Brownie contracts from the forge `./src` directory:
   ```bash
   $ make copy
   ```
2. Enter `deploy` directory (`cd deploy`)
3. Create and/or activate Python virtual env
   - Create: `python3.9 -m venv ve-venv`
   - NOTE: `eth-brownie` will fail to install on versions >= 3.10. The `eth-ape` library appears to be its successor but is not yet mature enough to migrate all tooling (Nov 1, 2023).
   - Activate: `. ve-venv/bin/activate`
   - Dependencies (first run): `pip install --upgrade pip && pip install -r requirements.txt`
4. Create an `.env` file with:
   ```
   INSTANCE_ID=primary
   ```
5. Populate JSON configurations with contract and multisig addresses
   - Mainnet: `./scripts/inputs/1/primary.json`
   - Polygon: `./scripts/inputs/137/primary.json`
   - Arbitrum: `./scripts/inputs/42161/primary.json`
6. Run deploy script: `brownie run scripts/mainnet/<script-name>.py --network mainnet`
   - NOTE: Some scripts depend on only `existing` (inputs) addresses, others depend on `existing` (inputs) and `deployed` (outputs) addresses. Outputs are set by other scripts.
   - Networks: `mainnet`, `polygon-main`, `arbitrum-main`

### Deploy (localhost)

To test the deployment, the Brownie scripts are run in conjunction with an anvil localnode using two terminal windows.

1. Populate JSON configurations with contract and multisig addresses: `./scripts/inputs/31337/primary.json`
2. (Terminal 1) Fork network with anvil: `anvil --fork-rpc-url <url> --fork-block-number <num> --chain-id 31337`
3. (Terminal 2) Run brownie script using development privkey: `brownie run scripts/mainnet/0_deploy_vedfx.py`

All scripts can be run using an Ethereum RPC with the block num `18415000`.

For different address configurations, change the chain `id` to easily use separate config files.

### Test Deployments (testnets)

For end-to-end testing of the sidechain contracts:

1. Replace Brownie contracts from the forge `./src` directory:
   ```bash
   $ make copy
   ```
2. Edit `./deploy/.env` with test wallet id

   - `DEPLOY_WALLET_ID=sepolia-dev`

3. Change dir: `cd deploy`
4. Activate Python virtual env: `source ve-venv/bin/activate`
5. Deploy fake LPT script: `brownie run scripts/testnet/deploy_fake_lpt.py --network sepolia`
   - Validate contract manually on `https://sepolia.etherscan.io`
6. Edit `scripts/testnet/deploy_child_chain_gauge.py` with LPT address
7. Deploy test child chain gauge set script: `brownie run scripts/testnet/deploy_child_chain_gauge.py --network sepolia`

### Compiling Vyper

```
$ vyper -f bytecode ChildChainStreamer.vy > streamer_bytecode.txt
```

### Documenting

Any contracts that failed to verify or must be verified manually (Vyper contracts) must be done on their respective block explorers (Etherscan, Polygonscan, Arbiscan). After deployment of any contract(s), new addresses are then to be added to the protocol addresses spreadsheet.
