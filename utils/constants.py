#!/usr/bin/env python
import math


WEEK = 86400 * 7
EMISSION_RATE = 1.9875488905e17
TOTAL_DFX_REWARDS = 5_118_750 * 1e18
EPOCHS_PER_YEAR = math.floor((365 * 24 * 60 * 60) / WEEK)
DFX_PRICE = 0.20
LP_PRICE = 1.00452
TOKENLESS_PRODUCTION = 40  # %, as hardcoded in contract
DEFAULT_GAUGE_TYPE = 0  # Ethereum stableswap pools
DEFAULT_TYPE_WEIGHT = 1e18
DEFAULT_GAUGE_WEIGHT = 1e18
