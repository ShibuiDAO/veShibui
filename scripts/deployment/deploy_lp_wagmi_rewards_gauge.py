import json

from brownie import (
    RewardStreamer,
    RewardsOnlyGauge,
    ERC20,
    accounts,
    ZERO_ADDRESS
)

from . import deployment_config as config


DAY = 86400

DECIMALS = 10 ** 18


# lp token, reward token, reward amount, reward duration
REWARD_POOL_TOKENS = {
    "SHIBUI-USDT<>WAGMIv3": (
        "0x3f714fe1380ee2204ca499d1d8a171cbdfc39eaa",  # SHIBUI-USDT pair
        "0xC6158B1989f89977bcc3150fC1F2eB2260F6cabE",  # WAGMI v3 options
        10_000 * DECIMALS,  # 10k WAGMI
        26 * DAY,  # May 5th -> May 31st = 26 days
    ),
}


def live():
    admin = accounts[0]
    deploy_part_one(admin, config.REWARDS_JSON)


def development():
    deploy_part_one(accounts[0])


def deploy_part_one(admin, rewards_json=None):
    rewards = {
        "RewardsOnlyGauge": {},
    }

    for (name, (lp_token, reward_token, reward_amount, reward_duration)) in REWARD_POOL_TOKENS.items():
        reward_token_c = ERC20.at(reward_token)
        streamer = RewardStreamer.deploy(admin, admin, reward_token, reward_duration, {"from": admin})
        gauge = RewardsOnlyGauge.deploy(
            admin, lp_token, {"from": admin}
        )

        reward_token_c.approve(streamer, reward_amount, {"from": accounts[0]})
        streamer.add_receiver(gauge, {"from": accounts[0]})

        coin_rewards = [reward_token] + [ZERO_ADDRESS] * 7
        gauge.set_rewards(streamer, streamer.get_reward.signature, coin_rewards, {"from": accounts[0]})

        rewards["RewardsOnlyGauge"][name] = {
            "streamer": streamer.contract_address,
            "gauge": gauge.contract_address,
        }

    if rewards_json is not None:
        with open(rewards_json, "w") as fp:
            json.dump(rewards, fp)
        print(f"Reward deployment addresses saved to {rewards_json}")
