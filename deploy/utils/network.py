#!/usr/bin/env python
from brownie import chain, network


connected_network = network.show_active()

is_localhost = chain.id in [1337, 31337]
