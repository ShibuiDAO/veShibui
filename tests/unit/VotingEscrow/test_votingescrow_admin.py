import brownie


def test_commit_admin_only(voting_escrow, accounts):
    with brownie.reverts("dev: admin only"):
        voting_escrow.commit_transfer_ownership(accounts[1], {"from": accounts[1]})
