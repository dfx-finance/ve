#!/usr/bin/env python

EMISSION_RATE = 1.9875488905e17
TOTAL_DFX_REWARDS = 5_118_750 * 1e18


NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "hardhat",
    "development",
    "ganache",
    "ganache-cli",
]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]
