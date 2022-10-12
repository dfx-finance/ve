#!/usr/bin/env python
# 1. Deploy new DfxDistributor with existing GaugeController
# 2. Update gauges with new distributor address for DFX rewards
# 3. Update frontend with new DfxDistributor address
from brownie import ZERO_ADDRESS, DfxDistributor, DfxUpgradeableProxy
import json
import time

from scripts import contracts
from scripts.helper import (
    get_addresses, 
    network_info,
    gas_strategy,
    DEPLOY_ACCT,
    PROXY_MULTISIG,
    GOVERNOR_MULTISIG,
    GUARDIAN_MULTISIG
)    


addresses = get_addresses()
connected_network, is_local_network = network_info()

REWARDS_RATE = 0
PREV_DISTRIBUTED_REWARDS = 0

output_data = {'replacementDistributor': {'logic': None, 'proxy': None}}

def main():
    should_verify = not is_local_network

    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)

    # 1. Deploy new DfxDistributor with existing GaugeController
    print(f'--- Deploying replacement Distributor contract to {connected_network} ---')
    dfx_distributor = DfxDistributor.deploy(
        {'from': DEPLOY_ACCT, 'gas_price': gas_strategy}, publish_source=should_verify)
    output_data['replacementDistributor']['logic'] = dfx_distributor.address

    print(
        f'--- Deploying Distributor proxy contract to {connected_network} ---')
    distributor_initializer_calldata = dfx_distributor.initialize.encode_input(
        addresses.DFX,
        gauge_controller.address,
        REWARDS_RATE,
        PREV_DISTRIBUTED_REWARDS,
        # needs another multisig to deal with access control behind proxy (ideally 2)
        GOVERNOR_MULTISIG,  # governor
        GUARDIAN_MULTISIG,  # guardian
        ZERO_ADDRESS   # delegate gauge for pulling type 2 gauge rewards
    )
    dfx_upgradable_proxy = DfxUpgradeableProxy.deploy(
        dfx_distributor.address,
        PROXY_MULTISIG,
        distributor_initializer_calldata,
        {'from': DEPLOY_ACCT, 'gas_price': gas_strategy},
        publish_source=should_verify,
    )
    output_data['replacementDistributor']['proxy'] = dfx_upgradable_proxy.address    

    # Write output to file
    with open(f'./scripts/redeployed_distributor_{int(time.time())}.json', 'w') as output_f:
        json.dump(output_data, output_f, indent=4)

    # Update gauge distributors
    gauges = contracts.gauges()
    for gauge in gauges:
        gauge.set_reward_distributor(addresses.DFX, dfx_upgradable_proxy.address, {'from': DEPLOY_ACCT, 'gas_price': gas_strategy})


if __name__ == "__main__":
    main()
