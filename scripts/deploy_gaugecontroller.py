from brownie import GaugeController, accounts
from brownie.network import gas_price
from brownie.network.gas.strategies import LinearScalingStrategy

import scripts.addresses as addresses


# Should there be separate types for 'amm' and 'dfxstable'?
DEFAUlT_GAUGE_TYPE = 'Liquidity'
DEFAULT_GAUGE_WEIGHT = 0

gas_strategy = LinearScalingStrategy('60 gwei', '150 gwei', 1.3)
gas_price(gas_strategy)


def main():
    acct = accounts.load('ganache')

    print('--- Deploying Gauge Controller contract to Ethereum mainnet ---')
    gauge_controller = GaugeController.deploy(
        addresses.DFX, addresses.VOTE_ESCROW, {'from': acct, 'gas_price': gas_strategy})

    print('----- Configure Gauge Controller with "Liquidity" type')
    gauge_controller.add_type(
        DEFAUlT_GAUGE_TYPE, 1e18, {'from': acct, 'gas_price': gas_strategy})

    print('--- Adding gauges for dfxStable pools on Curve.fi ---')
    gauge_controller.add_gauge(
        addresses.DFXCAD_CADC_LP, DEFAULT_GAUGE_WEIGHT, {'from': acct, 'gas_price': gas_strategy})
    gauge_controller.add_gauge(
        addresses.DFXSGD_XSGD_LP, DEFAULT_GAUGE_WEIGHT, {'from': acct, 'gas_price': gas_strategy})
