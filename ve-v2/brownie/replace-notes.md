```
rm scripts/*.json
brownie run 1_deploy_gaugecontroller.py --network hardhat
brownie run 2_deploy_distributor.py --network hardhat
brownie run 3_deploy_liquidity_gauges_v4.py --network hardhat

brownie run run/toggle_gauge_distributor.py --network hardhat
brownie run run/fastforward_chain.py --network hardhat
// brownie run run/poke_distributor_mining_parameters.py --network hardhat
```

# stake lpt w/ multiple users, mint dfx, lock up dfx and vote

```
brownie run hotfix/replace_distributor.py --network hardhat
```

# update addresses constants in ve and frontend

```
brownie run run/provide_distributor_rewards.py --network hardhat
brownie run run/log_ve_status.py --network hardhat
brownie run run/toggle_gauge_distributor.py --network hardhat
brownie run run/fastforward_chain.py --network hardhat
brownie run run/distribute_gauge_rewards.py --network hardhat
```
