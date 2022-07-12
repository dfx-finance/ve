# VeDFX Contracts

This veDFX is an implementation of Curve's Vote Escrow + Gauge contracts in Vyper. These use Vyper
for smart contract code and brownie + ganache for testing and deployments.
![veDFX](https://user-images.githubusercontent.com/25423613/178617916-680ef134-c076-4e9b-a946-c26b557d27f5.png)

#### References

1. https://eth-brownie.readthedocs.io
2. https://github.com/curvefi/curve-dao-contracts/

### Getting started:

1. Create Python virtual env

```bash
$ python3 -m venv ve-venv
```

2. Install dependencies

```bash
$ . ve-venv/bin/activate
$ pip install -r requirements.txt
$ npm install ganache
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

5. Run deploy script

```bash
$ brownie run deploy_gaugecontroller.py --network mainnet-fork
```
