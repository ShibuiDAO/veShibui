import json

from brownie import (
    VotingEscrow,
    accounts,
)

from . import deployment_config as config


def live_part_one():
    admin = accounts[0]
    deploy_part_one(admin, config.SHIBUI, config.DEPLOYMENTS_JSON)


def development():
    deploy_part_one(accounts[0])


def deploy_part_one(admin, token, deployments_json=None):
    voting_escrow = VotingEscrow.deploy(
        token,
        "Voting-escrowed SHIBUI",
        "veSHIBUI",
        {"from": admin},
    )

    deployments = {
        "VotingEscrow": voting_escrow.contract_address,
    }

    if deployments_json is not None:
        with open(deployments_json, "w") as fp:
            json.dump(deployments, fp)
        print(f"Deployment addresses saved to {deployments_json}")
