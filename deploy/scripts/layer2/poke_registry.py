from brownie import ChildChainRegistry
from utils.logger import load_inputs, load_outputs

from utils.config import DEPLOY_ACCT, INSTANCE_ID

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


def poke():
    registry = ChildChainRegistry.at(deployed.read_addr("gaugeRegistry"))
    registry.poke({"from": DEPLOY_ACCT})


def main():
    poke()
