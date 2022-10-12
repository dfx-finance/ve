to deploy:
brownie run 1_deploy_gaugecontroller.py --network hardhat
brownie run 2_deploy_distributor.py --network hardhat
brownie run 3_deploy_liquidity_gauges_v4.py --network hardhat

to activate:
brownie run run/provide_distributor_rewards.py --network hardhat
brownie run run/toggle_gauge_distributor.py --network hardhat
brownie run run/fastforward_chain.py --network hardhat
brownie run run/distribute_gauge_rewards.py --network hardhat

to check gauges received rewards after 1 epoch passes:
brownie run run/log_ve_status.py --network hardhat
