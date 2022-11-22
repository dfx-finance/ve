# VeDFX Contracts

This veDFX is an implementation of Curve's Vote Escrow + Gauge contracts in Vyper. These use Vyper
for smart contract code and brownie + ganache for testing and deployments.
![veDFX](https://user-images.githubusercontent.com/25423613/178617916-680ef134-c076-4e9b-a946-c26b557d27f5.png)

Implementation working doc: https://docs.google.com/document/d/1t5nprPEhhA1amXQ8VWf-PuXaP0dcPcHz2an-eM0Lg2o/

Calculations on VE emissions: https://docs.google.com/spreadsheets/d/1k1yAvAW_a6bHn4slPboGRl8ONsBEvO66YMWSOva_7MM/edit?usp=sharing

### References

1. https://eth-brownie.readthedocs.io
2. https://developers.angle.money/governance-and-cross-module-contracts/governance-contracts/gauge-controller
3. https://github.com/curvefi/curve-dao-contracts/

### External Audits

#### Curve:

1. https://curve.fi/files/00-ToB.pdf
2. https://curve.fi/files/01-ToB.pdf

#### Angle:

1. https://github.com/AngleProtocol/angle-core/blob/main/audits/Sigma%20Prime%20Audit%20Report%20July%2021.pdf
2. https://github.com/AngleProtocol/angle-core/blob/main/audits/Chainsecurity%20Audit%20Report%20December%2021.pdf

## Getting Started

### Local Node

Testing is designed to use the hardhat node configured in the `hh` directory:

```bash
$ npx hardhat node
```

### VE Dependencies

1. Create Python virtual env

   ```bash
   $ python3 -m venv ve-venv
   ```

2. Install build dependencies

   ```bash
   $ . ve-venv/bin/activate
   $ pip install -r requirements.txt
   ```

3. Install contract dependencies\*

   ```
   $ brownie pm install OpenZeppelin/openzeppelin-contracts@4.5.0
   $ brownie pm install OpenZeppelin/openzeppelin-contracts-upgradeable@4.5.0
   ```

4. Add remappings to VSCode's `settings.json` file for Solidity:

   ```
   "solidity.remappingsUnix": [
   "@openzeppelin/=/Users/kyle/.brownie/packages/OpenZeppelin/openzeppelin-contracts@4.5.0",
   "@openzeppelinUpgradeable/=/Users/kyle/.brownie/packages/OpenZeppelin/openzeppelin-contracts-upgradeable@4.5.0"
   ]
   ```

5. Add hardhat local private key to brownie (scripts will have to be adjusted accordingly, the default name used is `hardhat`). Most likely this will be account 0 coming from the standard Hardhat mnemonic `test test test test test test test test test test test junk`.

   ```bash
   $ brownie accounts new <account-name>
   # Enter private key
   # Enter account password (blank)
   ```

\*NOTE: Some developers may run into authentication issues with `brownie pm install` or other `brownie` commands. If so, you may add `GITHUB_TOKEN` to a `.env` file. The `.env.example` has an example and links to relevant documentation.

### Testing

Run an individual test with debug messages:

```bash
$ brownie test tests/<test_script_name>.py -s
```

### Deployment

1. Add deploy account to brownie by private key

   ```bash
   $ brownie accounts new deployve
   $ brownie accounts new deployve-proxyadmin
   ```

2. Edit deploy scripts (_step 3_) to load account with wallets named `deployve` and `deployve-proxyadmin`

3. Edit `gas_strategy` in `./scripts/helper.py` with recent gas prices from Etherscan

4. Deploy veDFX contract (if necessary)

   ```bash
   $ brownie run 0_deploy_vedfx.py --network <network-name>
   ```

5. Run VE deploy scripts

   ```bash
   $ brownie run 1_deploy_gaugecontroller.py --network <network-name>
   $ brownie run 2_deploy_distributor.py --network <network-name>
   $ brownie run 3_deploy_liquidity_gauges_v4.py --network <network-name>
   ```

_Networks:_

| Network  | Network Name   |
| -------- | -------------- |
| Ethereum | `ethereum`     |
| Polygon  | `polygon-main` |
| Hardhat  | `hardhat`      |

### Operation

- Logging state of VE to console

  ```bash
  $ brownie run run/log_ve_status.py --network <network-name>
  ```

- Provide rewards to the Distributor contract and activate gauges

  ```bash
  $ brownie run run/provide_distributor_rewards.py --network <network-name>
  ```

  _\*Edit `provide_distributor_rewards.py` script with amount of DFX rewards to add and its initial distribution rate before running_

- Activate distributions to gauges

  ```bash
  $ brownie run run/toggle_gauge_distributor.py --network <network-name>
  ```

- At start of new epoch:

  - (Public) Poke to update mining rate

    ```bash
    $ brownie run run/poke_distributor_mining_parameters.py --network <network-name>
    ```

  - (Private to Governor) Distribute rewards to all gauges

    ```bash
    $ brownie run run/distribute_gauge_rewards.py --network <network-name>
    ```

### Other

- Fast-forward local node to advance epoch

  ```bash
  $ brownie run run/fastforward_chain.py
  ```
