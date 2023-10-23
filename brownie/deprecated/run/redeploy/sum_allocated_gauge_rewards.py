#!/usr/bin/env python
from datetime import datetime

from brownie import accounts, chain, web3

from utils import contracts
from utils.gas import gas_strategy
from utils.network import get_network_addresses

HARDHAT_ACCT = accounts.load("hardhat")
addresses = get_network_addresses()

GAUGES_INFO = {
    "CADC/USDC": {
        "gauge_addr": addresses.DFX_CADC_USDC_GAUGE,
        "holders": [
            "0x193f0ee42a199a0cecd479a9f09ba293eb1ca357",
            "0x29770812d00e6c24de42d7f51274a05e6a3c04f0",
            "0xa2490947b30258b522b7d6fd8fabec2d21c42d57",
            "0x9ecf82bf1fe738fe5e41ab46f38e37781cbfb349",
            "0x70e439584ef1ba300106b9c16543eaa1de676dc2",
            "0x1867608e55a862e96e468b51dc6983bca8688f3d",
            "0x4b644be0c25fe19d95943937a4d1ae1156772d45",
            "0xef47003f0e276eb0fb60b626e80554dd7adcdd11",
            "0x07fe984c446417c1ff4532ce4fd67eeb59a0d682",
            "0x3d460eedc8c03e1efff7bccadc7113ca42f1c63c",
            "0x06a54385f41162ce11e52a807ab746f05e0cbf86",
            "0x678aff196d55d1d2474c103115847e5231f01df5",
        ],
    },
    "EUROC/USDC": {
        "gauge_addr": addresses.DFX_EUROC_USDC_GAUGE,
        "holders": [
            "0x9ecf82bf1fe738fe5e41ab46f38e37781cbfb349",
            "0x07fe984c446417c1ff4532ce4fd67eeb59a0d682",
            "0xfb27c8582976f1a29d58e89bcc89da1e54d78076",
            "0x6f9bb7e454f5b3eb2310343f0e99269dc2bb8a1d",
            "0x68b001552480932276cf9d5f4fff57877cec14a7",
            "0xfa8dc5fc2f212c754a440c93f7f23984cbb854d0",
            "0x0fb031ac06b6c83f7767dfd2a0e51a9f31672e9d",
        ],
    },
    "GYEN/USDC": {
        "gauge_addr": addresses.DFX_GYEN_USDC_GAUGE,
        "holders": [
            "0x9ecf82bf1fe738fe5e41ab46f38e37781cbfb349",
            "0x384ddba5a9e0b80aefdf73197f09f3b7b9c5a829",
            "0x87029960cb6d1011289d35bc8944d37b88c46b72",
            "0xeae3974c879fbeb83cdbe537737c519cbe8836da",
            "0xe71a95139b0c2dcd0a03cf355d972dc644969e1a",
            "0x93C9175E26F57d2888c7Df8B470C9eeA5C0b0A93",
        ],
    },
    "NZDS/USDC": {
        "gauge_addr": addresses.DFX_NZDS_USDC_GAUGE,
        "holders": [
            "0xf95d531c183622efc6c20da592078d7abc4aea03",
            "0x29770812d00e6c24de42d7f51274a05e6a3c04f0",
            "0x07fe984c446417c1ff4532ce4fd67eeb59a0d682",
            "0xeec2d3701acaf2689c229fab93a80e42e83e2088",
            "0xead6718ec938d82655918261005d5df57ccfb75e",
            "0x15b14afd3b7ad61da29fe975e14cc709eced0a4e",
            "0xd8942da20c0438d67a55ca4db93d08a8625ccd5d",
            "0xad9cbd4b9b1a9cc08b32e09a7961bf5b07e52bf3",
            "0x29431fec7a08fa02420c672468f3c6965a7fdc26",
            "0xad843763abb6a2fc2153cd72ac6288dcb5529b36",
            "0x171a296c4d3a1bd28c0e19f920d1ef8cd6a50daf",
        ],
    },
    "TRYB/USDC": {
        "gauge_addr": addresses.DFX_TRYB_USDC_GAUGE,
        "holders": [
            "0x9bfb3c8f18137e4a8dc3656aa160ee6c9b17befd",
            "0xcf7fea15b049ab04ffd03c86f353729c8519d72e",
            "0x6dfdd20a7b7080ddf8301250948c479fb23ed132",
            "0xa457549ff0bed5a952e2fbdf308478a73debd736",
            "0x8bf0de1eec190c9f61cb8f43550a426905e6f5ff",
            "0x29770812d00e6c24de42d7f51274a05e6a3c04f0",
            "0x9ecf82bf1fe738fe5e41ab46f38e37781cbfb349",
            "0x678aff196d55d1d2474c103115847e5231f01df5",
            "0x1b949538d6fff93ce28aa14a576bc6f2b04ee6b2",
            "0x383cdbcfa1249dc5220a3a84134d9ac95b10ce1a",
            "0x171a296c4d3a1bd28c0e19f920d1ef8cd6a50daf",
        ],
    },
    "XIDR/USDC": {
        "gauge_addr": addresses.DFX_XIDR_USDC_GAUGE,
        "holders": [
            "0x9ecf82bf1fe738fe5e41ab46f38e37781cbfb349",
            "0x391473f3E818e4B81ab0d1c58b7F5E827B780A86",
            "0x05b0E0b39309Bd0ffE8700cd91dEe76eBB1394ee",
            "0x11d67Fa925877813B744aBC0917900c2b1D6Eb81",
            "0xD178F2d93B92Ac47cf51a899463Eca8acC37A8D5",
            "0x1b04D574D4A3d57fb724848937a926aa21c59271",
        ],
    },
    "XSGD/USDC": {
        "gauge_addr": addresses.DFX_XSGD_USDC_GAUGE,
        "holders": [
            "0x52d302add37d197331ccacffbb2d1738a3909a1e",
            "0x07fe984c446417c1ff4532ce4fd67eeb59a0d682",
            "0x5c44368c0ad4c446842738bdbf8f2bbf9876546e",
            "0x6f9bb7e454f5b3eb2310343f0e99269dc2bb8a1d",
            "0x613260df13b773db743f976a1643a775452bd3e1",
            "0xab12253171a0d73df64b115cd43fe0a32feb9daa",
            "0x68b001552480932276cf9d5f4fff57877cec14a7",
        ],
    },
}


###
### Hardhat utilities
###
def fastforward_chain(until: datetime):
    chain.sleep(0)
    t0 = int(chain.time())
    chain.sleep(int(until.timestamp()) - t0)
    chain.mine()
    t1 = int(chain.time())

    orig = datetime.fromtimestamp(t0)
    new = datetime.fromtimestamp(t1)
    print("--- Fast-forward Chain -------------------------")
    print(f"Fastforwarded chain: {orig} --> {new}\n")


def main():
    dfx = contracts.erc20(addresses.DFX)

    for pair, info in GAUGES_INFO.items():
        logs = web3.eth.get_logs(
            {
                "address": "0xF8389313bb9317fd88692AdB657684FA5622b157",
                "fromBlock": 15747859,
                "toBlock": "latest",
                "topics": [
                    "0x7ecd84343f76a23d2227290e0288da3251b045541698e575a5515af4f04197a3"
                ],
            }
        )
        print(logs[0])
        print(len(logs))

        import sys

        sys.exit()

    fastforward_chain(datetime(2023, 6, 1))
    for pair, info in GAUGES_INFO.items():
        g = contracts.gauge(info["gauge_addr"])
        raw_dfx_rate = g.reward_data(addresses.DFX)[3]
        undistributed_dfx_rewards = raw_dfx_rate * 604800
        dfx_balance = dfx.balanceOf(g)
        print(
            f"{pair} reward balance: {undistributed_dfx_rewards / 1e18} DFX ({dfx_balance / 1e18} DFX in gauge)"
        )

        claimables = [
            g.claimable_reward(addr, addresses.DFX) for addr in info["holders"]
        ]
        total_claimed = sum(claimables)

        # claimed = []
        # for addr in info["holders"]:
        #     HARDHAT_ACCT.transfer(addr, "1 ether", gas_price=gas_strategy, silent=True)
        #     dfx_before = dfx.balanceOf(addr)
        #     user_balance = g.balanceOf(addr)
        #     g.withdraw(
        #         user_balance,
        #         True,
        #         {"from": addr, "gas_price": gas_strategy, "silent": True},
        #     )
        #     dfx_after = dfx.balanceOf(addr)
        #     dfx_rewards = dfx_after - dfx_before
        #     print(addr, dfx_rewards)
        #     claimed.append(dfx_rewards)
        # total_claimed = sum(claimed)
        leftover = dfx_balance - total_claimed
        print(f"\t{total_claimed / 1e18} DFX claimed, {leftover / 1e18} DFX leftover")


if __name__ == "main":
    main()
