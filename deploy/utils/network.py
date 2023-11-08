#!/usr/bin/env python
from brownie import chain, network
import dotenv
import os

dotenv.load_dotenv()


connected_network = network.show_active()

is_localhost = int(os.getenv("FORK", 0)) == 1 or chain.id in [1337, 31337, 31338]
