import logging
import pytest
from brownie_tokens import ERC20


def approx(a, b, precision=1e-10):
    if a == b == 0:
        return True
    return 2 * abs(a - b) / (a + b) <= precision


@pytest.fixture(scope="module")
def token(ERC20, accounts):
    yield ERC20.deploy("Shibui", "SHIBUI", 18, 50_000_000, {"from": accounts[0]})


@pytest.fixture(scope="module")
def voting_escrow(VotingEscrow, accounts, token):
    yield VotingEscrow.deploy(
        token, "Voting-escrowed SHIBUI", "veSHIBUI", {"from": accounts[0]}
    )


@pytest.fixture(scope="module")
def coin_reward():
    yield ERC20("Boba WAGMI v3 Option", "WAGMIv3", 18)


@pytest.fixture(scope="module")
def rewards_only_gauge(RewardsOnlyGauge, accounts, mock_lp_token):
    yield RewardsOnlyGauge.deploy(accounts[0], mock_lp_token, {"from": accounts[0]})


@pytest.fixture(scope="module")
def mock_lp_token(ERC20LP, accounts):
    yield ERC20LP.deploy("Oolong LP token", "OLP", 18, 10 ** 9, {"from": accounts[0]})


@pytest.fixture(scope="module")
def logger():
    yield logging.getLogger('Shibui')
