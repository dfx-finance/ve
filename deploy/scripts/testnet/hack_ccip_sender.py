from brownie import Contract, CcipSender, CcipSenderOld
from brownie import accounts, interface

from utils.config import DEPLOY_ACCT, DEPLOY_PROXY_ACCT, INSTANCE_ID
from utils.logger import load_inputs

# addr = "0x7ace867b3a503C6C76834ac223993FBD8963BED2"

existing = load_inputs(INSTANCE_ID)


def main():
    # provide proxy admin with gas
    accounts[0].transfer(DEPLOY_PROXY_ACCT, "5 ether")
    print(DEPLOY_PROXY_ACCT.balance())

    # get proxy for CCIPSender
    sender_proxy = Contract.from_abi(
        "DfxUpgradeableProxy",
        existing.read_addr("ccipSender"),
        interface.IDfxUpgradeableProxy.abi,
    )

    # new implementation
    ccip_sender_logic = CcipSender.deploy(
        existing.read_addr("DFX"),
        {"from": accounts[0]},
        # publish_source=VERIFY_CONTRACTS,
    )

    # upgrade implementation
    sender_proxy.upgradeTo(ccip_sender_logic.address, {"from": DEPLOY_PROXY_ACCT})

    sender = Contract.from_abi(
        "CcipSender", existing.read_addr("ccipSender"), CcipSender.abi
    )
    sender.initialize(
        existing.read_addr("ccipSender"), DEPLOY_ACCT, {"from": accounts[0]}
    )
    print(sender.admin())

    # call initialize as hacker

    junk = "0x8195D3496305D2DbE43B21d51e6cC77B6C9C8364"
    hacker = "0x6cC5F688a315f3dC28A7781717a9A798a59fDA7b"
    sender.initialize(junk, hacker, {"from": accounts[0]})
