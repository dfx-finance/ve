#!/usr/bin/env python
from brownie import veDFX

from utils.config import INSTANCE_ID
from utils.logger import load_inputs, load_outputs

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


def main():
    pass


if __name__ == "__main__":
    main()
