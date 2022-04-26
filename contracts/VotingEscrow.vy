# @version ^0.3.1

interface ERC20:
    def decimals() -> uint256: view
    def name() -> String[64]: view
    def symbol() -> String[32]: view
    def transfer(to: address, amount: uint256) -> bool: nonpayable
    def transferFrom(spender: address, to: address, amount: uint256) -> bool: nonpayable

event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address

token: public(address)

name: public(String[64])
symbol: public(String[32])
decimals: public(uint256)

admin: public(address)  # Can and will be a smart contract (Governor Charlie)
future_admin: public(address)

@external
def __init__(token_addr: address, _name: String[64], _symbol: String[32]):
    """
    @notice Contract constructor
    @param token_addr `SHIBUI` token address
    @param _name Token name
    @param _symbol Token symbol
    """
    self.admin = msg.sender
    self.token = token_addr

    _decimals: uint256 = ERC20(token_addr).decimals()
    assert _decimals <= 255
    self.decimals = _decimals

    self.name = _name
    self.symbol = _symbol

@external
def commit_transfer_ownership(addr: address):
    """
    @notice Transfer ownership of VotingEscrow contract to `addr`
    @param addr Address to have ownership transferred to
    """
    assert msg.sender == self.admin  # dev: admin only
    self.future_admin = addr
    log CommitOwnership(addr)


@external
def apply_transfer_ownership():
    """
    @notice Apply ownership transfer
    """
    assert msg.sender == self.admin  # dev: admin only
    _admin: address = self.future_admin
    assert _admin != ZERO_ADDRESS  # dev: admin not set
    self.admin = _admin
    log ApplyOwnership(_admin)
