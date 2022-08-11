#!/usr/bin/env python
from utils import gas_strategy

WEEK = 86400 * 7
EMISSION_RATE = 1.60345055442863e16
TOTAL_DFX_REWARDS = 1_248_560 * 1e18


def deposit_to_ve(dfx, voting_escrow, user_accounts, st_deposits, st_length, timestamp):
    for i, acct in enumerate(user_accounts):
        dfx.approve(voting_escrow, st_deposits[i],
                    {'from': acct, 'gas_price': gas_strategy})

        voting_escrow.create_lock(
            st_deposits[i], timestamp + (st_length[i] * WEEK), {'from': acct, 'gas_price': gas_strategy})


def submit_ve_votes(gauge_controller, gauges, user_accounts, st_votes):
    votes = []
    for i, acct in enumerate(user_accounts):
        votes.append([x * 1000 for x in st_votes[i]])
        # Use remainder of 100.00% on last vote(?)
        # Source comment: "XXX what if votes are not used up to 100%?"
        votes[-1].append(10000 - sum(votes[-1]))

        for x in range(3):
            gauge_controller.vote_for_gauge_weights(
                gauges[x], votes[-1][x], {'from': acct, 'gas_price': gas_strategy})
    return votes


def submit_ve_vote(gauge_controller, gauges, vote, account):
    for x in range(len(gauges)):
        gauge_controller.vote_for_gauge_weights(
            gauges[x], vote[x], {'from': account, 'gas_price': gas_strategy})


def calculate_ve_slope_data(voting_escrow, user_accounts, st_length, timestamp):
    slope_data = []
    for i, acct in enumerate(user_accounts):
        initial_bias = voting_escrow.get_last_user_slope(
            acct) * (voting_escrow.locked(acct)[1] - timestamp)
        duration = (
            timestamp + st_length[i] * WEEK
        ) // WEEK * WEEK - timestamp  # <- endtime rounded to whole weeks
        slope_data.append((initial_bias, duration))
    return slope_data
