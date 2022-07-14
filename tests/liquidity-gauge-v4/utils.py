from brownie.network.gas.strategies import LinearScalingStrategy

import addresses

DEFAULT_GAUGE_TYPE = 0  # Ethereum stableswap pools
DEFAULT_TYPE_WEIGHT = 1e18
DEFAULT_GAUGE_WEIGHT = 0
WEEK = 86400 * 7

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('30 gwei', '250 gwei', 1.3)


def setup_gauges(gauge_controller, gauges, master_account):
    gauge_controller.add_type(
        'AMM Liquidity Pools', DEFAULT_TYPE_WEIGHT, {'from': master_account, 'gas_price': gas_strategy})
    for gauge in gauges:
        gauge_controller.add_gauge(
            gauge, DEFAULT_GAUGE_TYPE, DEFAULT_GAUGE_WEIGHT, {'from': master_account, 'gas_price': gas_strategy})


def mint_dfx(dfx, amount, account):
    print("Account DFX balance (pre-mint):",
          dfx.balanceOf(account) / 1e18)
    account.transfer(addresses.DFX_MULTISIG,
                     '10 ether',
                     gas_price=gas_strategy)
    dfx.mint(account, amount,
             {'from': addresses.DFX_MULTISIG, 'gas_price': gas_strategy})
    print("Account DFX balance (post-mint):",
          dfx.balanceOf(account) / 1e18)


def send_dfx(dfx, amount, from_account, to_account):
    dfx.transfer(to_account, amount, {
                 'from': from_account, 'gas_price': gas_strategy})
    print("Sender account DFX balance:",
          dfx.balanceOf(from_account) / 1e18)


def deposit_to_ve(voting_escrow, user_accounts, st_deposits, st_length, timestamp):
    for i, acct in enumerate(user_accounts):
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
