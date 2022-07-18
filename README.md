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

### Getting started:

1. Create Python virtual env

```bash
$ python3 -m venv ve-venv
```

2. Install dependencies

```bash
$ . ve-venv/bin/activate
$ pip install -r requirements.txt
$ npm install ganache (*)
```

_\*Due to difficulties with ganache, `yarn hh:node` is now being used from the `frontend-monorepo`. Hardhat is able to use the same settings as `anvil` contained in these scripts._

```
$ brownie pm install OpenZeppelin/openzeppelin-contracts@4.5.0
$ brownie pm install OpenZeppelin/openzeppelin-contracts-upgradeable@4.5.0
```

NOTE: Some developers may run into authentication issues with `brownie pm install` or other `brownie` commands. If so, you may add `GITHUB_TOKEN` to a `.env` file. The `.env.example` has an example and links to relevant documentation.

Add remappings to VSCode's `settings.json` file for Solidity:

```
"solidity.remappingsUnix": [
  "@openzeppelin/=/Users/kyle/.brownie/packages/OpenZeppelin/openzeppelin-contracts@4.5.0"
]
```

3. Add ganache local private key to brownie

```bash
$ brownie accounts new <account-name>
# Enter private key
# Enter account password (blank)
```

4. Run tests at block num 14957500

```bash
(terminal 1) $ npm ganache -d --fork <ETH_RPC_URL>@14957500 --unlock 0x27E843260c71443b4CC8cB6bF226C3f77b9695AF
(terminal 2) $ brownie test --network mainnet-fork
```

Or to run a single test with debug messages:

```bash
(terminal 2) $ brownie test tests/<test_script_name>.py --network mainnet-fork -s
```

5. Run deploy script

```bash
$ brownie run deploy_gauges.py --network mainnet-fork
$ brownie run deploy_gaugecontroller.py --network mainnet-fork
```

## Testing

Tests can be run as a suite with:

```bash
$ brownie tests
```

Or tests can be run individually with verbose output, like:

```bash
$ brownie test tests/test_distribution_to_gauges.py -s
```
