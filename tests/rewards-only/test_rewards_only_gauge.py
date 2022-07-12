from brownie import ZERO_ADDRESS, chain
from brownie.network.gas.strategies import LinearScalingStrategy
import pytest

import addresses

WEEK = 86400 * 7
DEFAULT_GAUGE_TYPE = 0  # Ethereum stableswap pools

# Setting gas price is always necessary for deploy
# https://stackoverflow.com/questions/71341281/awaiting-transaction-in-the-mempool
gas_strategy = LinearScalingStrategy('30 gwei', '250 gwei', 1.3)


# handle setup logic required for each unit test
@pytest.fixture(scope='module', autouse=True)
def setup(dfx, gauge_controller, voting_escrow, three_gauges, three_staking_rewards, master_account, user_accounts):
    # Setup gauges
    gauge_controller.add_type(
        'Liquidity', 1e18, {'from': master_account, 'gas_price': gas_strategy})
    for gauge in three_gauges:
        gauge_controller.add_gauge(
            gauge, DEFAULT_GAUGE_TYPE, {'from': master_account, 'gas_price': gas_strategy})

    # Set rewards contract on gauge
    # https://curve.readthedocs.io/dao-gauges.html#setting-the-rewards-contract
    for i, gauge in enumerate(three_gauges):
        staking_rewards = three_staking_rewards[i]
        sigs = [staking_rewards.signatures['stake'],
                staking_rewards.signatures['withdraw'],
                staking_rewards.signatures['getReward']]
        sigs = "".join(i[2:] for i in sigs)
        sigs = "0x" + sigs + ("00" * 20)
        gauge.set_rewards(staking_rewards, sigs, [
                          dfx] + [ZERO_ADDRESS] * 7, {'from': master_account, 'gas_price': gas_strategy})

    # Mint some rewards
    rewards_per_gauge = 20000
    rewards_total = rewards_per_gauge * len(three_staking_rewards) * 1e18
    print("Master account DFX balance (pre-mint):",
          dfx.balanceOf(master_account) / 1e18)
    master_account.transfer(addresses.DFX_MULTISIG,
                            '10 ether',
                            gas_price=gas_strategy)
    dfx.mint(master_account, rewards_total,
             {'from': addresses.DFX_MULTISIG, 'gas_price': gas_strategy})
    print("Master account DFX balance (post-mint):",
          dfx.balanceOf(master_account) / 1e18)

    # Distribute rewards to each staking contract
    for staking_rewards in three_staking_rewards:
        print("hello")
        dfx.transfer(staking_rewards, rewards_per_gauge, {
                     'from': master_account, 'gas_price': gas_strategy})
        staking_rewards.notifyRewardAmount(
            rewards_per_gauge, {'from': master_account, 'gas_price': gas_strategy})
    print("Master account DFX balance (post-topup):",
          dfx.balanceOf(master_account) / 1e18)

    # # Init 10 s before the week change
    # t0 = chain.time()
    # t1 = (t0 + 2 * WEEK) // WEEK * WEEK - 10
    # chain.sleep(t1 - t0)

    # for acct in user_accounts:
    #     dfx.transfer(acct, 10e23,
    #                  {'from': master_account, 'gas_price': gas_strategy})
    #     dfx.approve(voting_escrow, 10e24,
    #                 {'from': acct, 'gas_price': gas_strategy})

    # # Deposit
    # timestamp = t1
    # st_deposits = [1000000000000000000079,
    #                1000000000000000000150, 1000000000000000008880]
    # st_length = [52, 52, 52]
    # for i, acct in enumerate(user_accounts):
    #     voting_escrow.create_lock(
    #         st_deposits[i], timestamp + (st_length[i] * WEEK), {'from': acct, 'gas_price': gas_strategy})

    # # Vote
    # st_votes = [[4, 3], [1, 4], [0, 3]]
    # votes = []
    # for i, acct in enumerate(user_accounts):
    #     votes.append([x * 1000 for x in st_votes[i]])
    #     # Use remainder of 100.00% on last vote(?)
    #     # Source comment: "XXX what if votes are not used up to 100%?"
    #     votes[-1].append(10000 - sum(votes[-1]))

    #     for x in range(3):
    #         gauge_controller.vote_for_gauge_weights(
    #             three_gauges[x], votes[-1][x], {'from': acct, 'gas_price': gas_strategy})

    # # Fast-forward chain
    # chain.sleep(WEEK * 4)


def test_claim_rewards(three_gauges, user_accounts):
    for acct in user_accounts:
        for gauge in three_gauges:
            # print(acct, gauge)
            # print(gauge.reward_contract())
            break
        break
