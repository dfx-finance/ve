# VeDFX Contracts

This veDFX is an implementation of Curve's Vote Escrow + Gauge contracts in Vyper. These use Vyper
for smart contract code and brownie + ganache for testing and deployments.

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

3. Run tests at block num 14957500

```bash
(terminal 1) $ npm ganache-cli -d --fork <ETH_RPC_URL>@14957500
(terminal 2) $ brownie test
```

4. Run deploy script

```bash
$ brownie run deploy_gaugecontroller.py
```
