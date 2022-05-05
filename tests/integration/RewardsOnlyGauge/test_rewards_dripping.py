from tests.conftest import approx
from brownie import ZERO_ADDRESS, chain

DAY = 86400
EPOCHS = int(25)

DECIMALS = 10 ** 18
WAGMI_DISTRIBUTION = 10_000 * DECIMALS

def test_rewards_dripping(
    accounts,
    RewardStreamer,
    rewards_only_gauge,
    mock_lp_token,
    coin_reward,
):
    # fund accounts to be used in the test
    for acct in accounts[1:5]:
        mock_lp_token.transfer(acct, 10 ** 21, {"from": accounts[0]})

    # approve liquidity_gauge from the funded accounts
    for acct in accounts[:5]:
        mock_lp_token.approve(rewards_only_gauge, 2 ** 256 - 1, {"from": acct})

    # configure streamer
    streamer = RewardStreamer.deploy(accounts[0], accounts[0], coin_reward, DAY * EPOCHS, {"from": accounts[0]})
    streamer.add_receiver(rewards_only_gauge, {"from": accounts[0]})

    coin_reward.approve(streamer, 2 ** 256 - 1, {"from": accounts[0]})
    coin_reward._mint_for_testing(accounts[0], WAGMI_DISTRIBUTION, {"from": accounts[0]})

    # deposit using 2 users at a 1:2 ratio (total 1.5 shares, 3 points)
    rewards_only_gauge.deposit(0.5 * DECIMALS, {"from": accounts[1]})
    rewards_only_gauge.deposit(1 * DECIMALS, {"from": accounts[2]})

    # depositors should get gauge tokens in their proportion
    assert rewards_only_gauge.balanceOf(accounts[1]) == 0.5 * DECIMALS
    assert rewards_only_gauge.balanceOf(accounts[2]) == 1 * DECIMALS

    # users should have no claimed rewards when using default "deposit" params
    assert rewards_only_gauge.claimed_reward(accounts[1], coin_reward) == 0
    assert rewards_only_gauge.claimed_reward(accounts[2], coin_reward) == 0

    # create list of possible rewards (in most cases just WAGMI)
    coin_rewards = [coin_reward] + [ZERO_ADDRESS] * 7
    # configure streamer signature and reward tokens
    rewards_only_gauge.set_rewards(streamer, streamer.get_reward.signature, coin_rewards, {"from": accounts[0]})

    streamer.notify_reward_amount(WAGMI_DISTRIBUTION, {"from": accounts[0]})

    # streamer should now hold the allocation
    assert coin_reward.balanceOf(streamer) == WAGMI_DISTRIBUTION

    chain.sleep(DAY)

    a1_balance = coin_reward.balanceOf(accounts[1])
    a2_balance = coin_reward.balanceOf(accounts[2])

    rewards_only_gauge.claim_rewards({"from": accounts[1]})
    rewards_only_gauge.claim_rewards({"from": accounts[2]})

    reward_fraction = (WAGMI_DISTRIBUTION / EPOCHS) / 3
    assert approx(coin_reward.balanceOf(accounts[1]) - a1_balance, reward_fraction, 1e-5)
    assert approx(coin_reward.balanceOf(accounts[2]) - a2_balance, reward_fraction * 2, 1e-5)

    chain.sleep(DAY)

    a1_balance = coin_reward.balanceOf(accounts[1])
    a2_balance = coin_reward.balanceOf(accounts[2])

    rewards_only_gauge.claim_rewards({"from": accounts[1]})
    rewards_only_gauge.claim_rewards({"from": accounts[2]})

    reward_fraction = (WAGMI_DISTRIBUTION / EPOCHS) / 3
    assert approx(coin_reward.balanceOf(accounts[1]) - a1_balance, reward_fraction, 1e-5)
    assert approx(coin_reward.balanceOf(accounts[2]) - a2_balance, reward_fraction * 2, 1e-5)

