# Testing

## Run Tests

Run a specific test file with debug messages:

```bash
$ brownie test tests/<test_script_name>.py -s
```

### Forking Mainnet (for testing live contracts)

```bash
$ anvil --fork-url https://eth-mainnet.g.alchemy.com/v2/dRYOSLDw-_H1uT1bUtFKXipGKvKB1IX1 --fork-block-number 18366380
```

## VE Dependencies

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

4. Add hardhat local private key to brownie (scripts will have to be adjusted accordingly, the default name used is `hardhat`).

   Most likely this will be account 0 coming from the standard Hardhat mnemonic `test test test test test test test test test test test junk`.

   ```bash
   $ brownie accounts new <account-name>
   # Enter private key
   # Enter account password (blank)
   ```

\*NOTE: Some developers may run into authentication issues with `brownie pm install` or other `brownie` commands. If so, you may add `GITHUB_TOKEN` to a `.env` file. The `.env.example` has an example and links to relevant documentation.

### Test Files

- `./tests/test_apr_unboosted.py`:
- `./tests/test_apr_boosted.py`:
- `./tests/test_apr_max_boost.py`:
- `./tests/test_no_rewards_without_lp.py`:
- `./tests/test_rewards_unboosted.py`:
- `./tests/test_rewards_boosted.py`:
- `./tests/test_gauge_voting.py`:
- `./tests/test_distribution_to_gauges.py`:
- `./tests/test_emission_reduction_rate.py`:
- `./tests/test_rewards_two_distributors.py`:
- `./tests/test_theoretical_vs_actual.py`:
- `./tests/run_full_model.py`:
