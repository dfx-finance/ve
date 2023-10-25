#!/usr/bin/env python
from brownie import InterfaceIds
from utils.gas import gas_strategy

from fork.utils.account import DEPLOY_ACCT


def main():
    ids: InterfaceIds = InterfaceIds.deploy(
        {"from": DEPLOY_ACCT, "gas_price": gas_strategy}
    )
    msg_receiver_id, erc165_id = ids.getInterfaceIds()
    print(f"IAny2EVMMessageReceiver ID: {msg_receiver_id}")
    print(f"IERC165 ID: {erc165_id}")
