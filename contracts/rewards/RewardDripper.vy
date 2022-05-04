# @version ^0.3.1

from vyper.interfaces import ERC20


event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address

event ConfigureEpoch:
    epochs: uint256
    balance_snapshot: uint256
    drip_per: uint256

event Dripped:
    receiver: indexed(address)
    amount: uint256

event DripperKilled:
    pass


reward_token: public(address)
reward_receiver: public(address)

epochs: public(uint256)
reward_token_balance_snapshot: public(uint256)
drip_per_epoch: public(uint256)

admin: public(address)
future_admin: public(address)  # Can be a smart contract

kill: public(bool)


@external
def __init__(_admin: address, _reward_token: address, _reward_receiver: address):
    """
    @notice Contract constructor
    @param _admin Admin who can snapshot the balance.
    @param _reward_token Reward Token contract address.
    @param _reward_receiver Rewards Gauge address.
    """

    self.reward_token = _reward_token
    self.reward_receiver = _reward_receiver
    self.admin = _admin


@external
def commit_transfer_ownership(addr: address):
    """
    @notice Transfer ownership of GaugeController to `addr`.
    @param addr Address to have ownership transferred to.
    """
    assert msg.sender == self.admin  # dev: admin only

    self.future_admin = addr
    log CommitOwnership(addr)


@external
def accept_transfer_ownership():
    """
    @notice Accept a pending ownership transfer.
    """
    _admin: address = self.future_admin
    assert msg.sender == _admin  # dev: future admin only

    self.admin = _admin
    self.future_admin = ZERO_ADDRESS

    log ApplyOwnership(_admin)


@external
def kill_drip():
    """
    @notice Kill the drip mechanism.
    """
    assert msg.sender == self.admin  # dev: admin only

    self.kill = True
    log DripperKilled()


@external
def configure_epochs(_epochs: uint256):
    assert msg.sender == self.admin  # dev: admin only

    self.epochs = _epochs
    self.reward_token_balance_snapshot = ERC20(self.reward_token).balanceOf(self)
    self.drip_per_epoch = self.reward_token_balance_snapshot / self.epochs

    log ConfigureEpoch(self.epochs, self.reward_token_balance_snapshot, self.drip_per_epoch)


@external
def drip():
    assert msg.sender == self.reward_receiver  # dev: reward receiver only
    if self.kill == True:
        return

    ERC20(self.reward_token).transfer(self.reward_receiver, self.drip_per_epoch)
    log Dripped(self.reward_receiver, self.drip_per_epoch)
