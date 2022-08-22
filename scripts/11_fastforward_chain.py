#!/usr/bin/env python
import brownie
from brownie import chain

from scripts import addresses
from scripts.helper import gas_strategy, get_json_address

WEEK = 86400 * 7


def main():
    dfx_distributor_address = get_json_address(
        'deployed_distributor', ['distributor', 'proxy'])

    # fast-forward chain until end of epoch 1
    t0 = chain.time()
    t1 = (t0 + 2 * WEEK) // WEEK * WEEK - 10
    chain.sleep(t1 - t0)

    # unlock multisig account
    brownie.rpc.unlock_account(addresses.DFX_MULTISIG)

    # distribute rewards to gauges
    gauges = [
        addresses.DFX_CADC_USDC_LP,
        addresses.DFX_EUROC_USDC_LP,
        addresses.DFX_EURS_USDC_LP,
        addresses.DFX_NZDS_USDC_LP,
        addresses.DFX_TRYB_USDC_LP,
        addresses.DFX_XIDR_USDC_LP,
        addresses.DFX_XSGD_USDC_LP,
    ]
    distributor = brownie.interface.IDfxDistributor(dfx_distributor_address)
    distributor.distributeRewardToMultipleGauges(
        gauges, {'from': addresses.DFX_MULTISIG, 'gas_price': gas_strategy})


if __name__ == '__main__':
    main()
