#!/usr/bin/env python
import math


WEEK = 86400 * 7
EMISSION_RATE = 3.312581483e17
TOTAL_DFX_REWARDS = 8_531_250 * 1e18
EPOCHS_PER_YEAR = math.floor((365 * 24 * 60 * 60) / WEEK)
DFX_PRICE = 0.44
LP_PRICE = 1.00452
TOKENLESS_PRODUCTION = 40  # %, as hardcoded in contract
DEFAULT_GAUGE_TYPE = 0  # Ethereum stableswap pools
DEFAULT_TYPE_WEIGHT = 1e18
DEFAULT_GAUGE_WEIGHT = 1e18
