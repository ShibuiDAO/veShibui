import pytest

@pytest.fixture(scope="module")
def token(ERC20, accounts):
    yield ERC20.deploy("Shibui", "SHIBUI", 18, 50_000_000, {"from": accounts[0]})


@pytest.fixture(scope="module")
def voting_escrow(VotingEscrow, accounts, token):
    yield VotingEscrow.deploy(
        token, "Voting-escrowed SHIBUI", "veSHIBUI", {"from": accounts[0]}
    )
