from brownie import DfxDistributor, DfxUpgradableProxy, accounts
from brownie.network import gas_price
from brownie.network.gas.strategies import LinearScalingStrategy
import scripts.addresses as addresses

from scripts.helper import encode_function_data

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('80 gwei', '250 gwei', 2.0)

def main():
    acct = accounts[0]

    print('--- Deploying Distributor contract to Ethereum mainnet ---')
    dfx_distributor = DfxDistributor.deploy({'from': acct, 'gas_price': gas_strategy})

    distributor_initializer_calldata = encode_function_data(
        addresses.DFX,
        addresses.DFX, # gauge controller addresss
        1,
        100,
        addresses.DFX_MULTISIG, # should consider using another multisig to deal with access control
        addresses.DFX_MULTISIG, 
        addresses.DFX_MULTISIG
    )

    dfx_upgradable_proxy = DfxUpgradableProxy.deploy(
        dfx_distributor.address,
        addresses.DFX_MULTISIG,
        distributor_initializer_calldata
    )