# VeDFX Contracts

This veDFX is an implementation of Curve's Vote Escrow + Gauge contracts in Vyper. These use Vyper
for smart contract code and brownie + ganache for testing and deployments.
![veDFX](https://user-images.githubusercontent.com/25423613/178617916-680ef134-c076-4e9b-a946-c26b557d27f5.png)

Implementation working doc: https://docs.google.com/document/d/1t5nprPEhhA1amXQ8VWf-PuXaP0dcPcHz2an-eM0Lg2o/

Calculations on VE emissions: https://docs.google.com/spreadsheets/d/1k1yAvAW_a6bHn4slPboGRl8ONsBEvO66YMWSOva_7MM/edit?usp=sharing

#### References

1. https://eth-brownie.readthedocs.io
2. https://developers.angle.money/governance-and-cross-module-contracts/governance-contracts/gauge-controller
3. https://github.com/curvefi/curve-dao-contracts/

#### External Audits

##### Curve:

1. https://curve.fi/files/00-ToB.pdf
2. https://curve.fi/files/01-ToB.pdf

##### Angle:

1. https://github.com/AngleProtocol/angle-core/blob/main/audits/Sigma%20Prime%20Audit%20Report%20July%2021.pdf
2. https://github.com/AngleProtocol/angle-core/blob/main/audits/Chainsecurity%20Audit%20Report%20December%2021.pdf

### Getting started:

1. Create Python virtual env

```bash
$ python3 -m venv ve-venv
```

2. Install dependencies

```bash
$ . ve-venv/bin/activate
$ pip install -r requirements.txt
```

_\*Due to difficulties with ganache, `yarn hh:node` is now being used from the `frontend-monorepo`. Hardhat is able to use the same settings as `anvil` contained in these scripts. Edit: It appears that while Brownie may be able to launch and interact with Anvil using default settings,
it is not able to attach to instances running independently. This is evidenced [here](https://github.com/eth-brownie/brownie/blob/4ae5f527ea86eb95766fe225a0f67620ffd36022/brownie/network/rpc/__init__.py#L23); when this is updated in brownie's source, we may then be able
to use it for local testing as a drop-in for hardhat on this repo_

```
$ brownie pm install OpenZeppelin/openzeppelin-contracts@4.5.0
$ brownie pm install OpenZeppelin/openzeppelin-contracts-upgradeable@4.5.0
```

NOTE: Some developers may run into authentication issues with `brownie pm install` or other `brownie` commands. If so, you may add `GITHUB_TOKEN` to a `.env` file. The `.env.example` has an example and links to relevant documentation.

Add remappings to VSCode's `settings.json` file for Solidity:

```
"solidity.remappingsUnix": [
  "@openzeppelin/=/Users/kyle/.brownie/packages/OpenZeppelin/openzeppelin-contracts@4.5.0",
  "@openzeppelinUpgradeable/=/Users/kyle/.brownie/packages/OpenZeppelin/openzeppelin-contracts-upgradeable@4.5.0"
]
```

3. Add hardhat local private key to brownie (scripts will have to be adjusted accordingly, the default name used is `hardhat`). Most likely this will be account 0 coming from the standard Hardhat mnemonic `test test test test test test test test test test test junk`.

```bash
$ brownie accounts new <account-name>
# Enter private key
# Enter account password (blank)
```

4. **Testing:**.py Run tests at block num 15051000
   Using hardhat node from frontend repo:

```bash
(terminal 1: frontend-monorepo) $ yarn hh:node
(terminal 2: ve) $ brownie test
```

or with ganache-cli:

```bash
(terminal 1) $ npm ganache -d --fork <ETH_RPC_URL>@15051000 --unlock 0x27E843260c71443b4CC8cB6bF226C3f77b9695AF
(terminal 2) $ brownie test
```

Or to run a single test with debug messages:

```bash
(terminal 2) $ brownie test tests/<test_script_name>.py -s
```

5. **Deployment:** Run deploy script

   1. Add deploy account brownie by private key

   ```bash
   $ brownie accounts new deployve
   $ brownie accounts new deployve-proxyadmin
   ```

   2. Edit deploy scripts in _step 3_ to load account with wallets `deployve` and `deployve-proxyadmin`

   3. Edit `gas_strategy` in `./scripts/helper.py` with recent gas prices from Etherscan

   4. Deploy veDFX contract if necessary

   ```bash
   $ brownie run 99_deploy_vedfx.py --network <network-name>
   ```

   5. Run deploy scripts
      Polygon:

   ```bash
   $ brownie run 1_deploy_gaugecontroller.py --network polygon-main
   $ brownie run 2_deploy_distributor.py --network polygon-main
   $ brownie run 3_deploy_liquidity_gauges_v4.py --network polygon-main
   ```

   Ethereum:

   ```bash
   $ brownie run 1_deploy_gaugecontroller.py --network ethereum
   $ brownie run 2_deploy_distributor.py --network ethereum
   $ brownie run 3_deploy_liquidity_gauges_v4.py --network ethereum
   ```

6. **Operation:**

   1. Print current state of VE to console

   ```bash
   $ brownie run run/log_ve_status.py --network <network-name>
   ```

   2. Provide rewards to the Distributor contract and activate gauges (edit with DFX rewards to add and initial distribution rate)

   ```bash
   $ brownie run run/provide_distributor_rewards.py --network <network-name>
   ```

   3. Activate distributions

   ```bash
   $ brownie run run/toggle_gauge_distributor.py --network <network-name>
   ```

   4. Print current state of VE to console again to verify

   5. Once next epoch is begun:

      - (Public) Poke to update mining rate

      ```bash
      $ brownie run run/poke_distributor_mining_rewards.py --network <network-name>
      ```

      - (Private to Governor) Distribute rewards to all gauges

      ```bash
      $ brownie run run/distribute_gauge_rewards.py --network <network-name>
      ```

7. **Local testing (hardhat only):**

   1. Fast-forward chain until end of epoch 1

   ```bash
   $ brownie run run/fastforward_chain.py
   ```
