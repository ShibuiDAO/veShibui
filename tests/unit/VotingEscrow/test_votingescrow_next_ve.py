import brownie
from brownie import ZERO_ADDRESS


def test_commit_admin_only(voting_escrow, accounts):
    with brownie.reverts("dev: admin only"):
        voting_escrow.commit_next_ve_contract(accounts[1], {"from": accounts[1]})


def test_apply_admin_only(voting_escrow, accounts):
    with brownie.reverts("dev: admin only"):
        voting_escrow.apply_next_ve_contract({"from": accounts[1]})


def test_commit_next_ve(voting_escrow, accounts):
    assert voting_escrow.migration() == False

    voting_escrow.commit_next_ve_contract(accounts[1], {"from": accounts[0]})

    assert voting_escrow.next_ve_contract() == ZERO_ADDRESS
    assert voting_escrow.queued_next_ve_contract() == accounts[1]
    assert voting_escrow.migration() == False


def test_apply_next_ve(voting_escrow, accounts):
    assert voting_escrow.migration() == False

    voting_escrow.commit_next_ve_contract(accounts[1], {"from": accounts[0]})
    voting_escrow.apply_next_ve_contract({"from": accounts[0]})

    assert voting_escrow.queued_next_ve_contract() == ZERO_ADDRESS
    assert voting_escrow.next_ve_contract() == accounts[1]
    assert voting_escrow.migration() == True


def test_apply_without_commit(voting_escrow, accounts):
    with brownie.reverts():
        voting_escrow.apply_transfer_ownership({"from": accounts[1]})
