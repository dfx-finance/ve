#!/usr/bin/env python
import math

WEEK = 86400 * 7
SECONDS_PER_YEAR = 365 * 24 * 60 * 60
EPOCHS_PER_YEAR = math.floor((365 * 24 * 60 * 60) / WEEK)

DFX_PRICE = 0.20
LP_PRICE = 1.00452
TOKENLESS_PRODUCTION = 40  # %, as hardcoded in contract
DEFAULT_GAUGE_TYPE = 0  # Ethereum stableswap pools
DEFAULT_TYPE_WEIGHT = 1e18
DEFAULT_GAUGE_WEIGHT = 1e18

MAX_UINT256 = 2**256 - 1
