from tests.conftest import approx

H = 3600
DAY = 86400
WEEK = 7 * DAY
MAXTIME = 7 * 4 * 6 * DAY
TOL = 120 / WEEK

def test_voting_powers(web3, chain, accounts, token, voting_escrow):

    a0, a1 = accounts[:2]
    amount = 1000 * 10 ** 18
    token.transfer(a1, amount, {"from": a0})
    stages = {}

    token.approve(voting_escrow.address, amount * 10, {"from": a0})
    token.approve(voting_escrow.address, amount * 10, {"from": a1})

    assert voting_escrow.totalSupply() == 0
    assert voting_escrow.balanceOf(a1) == 0
    assert voting_escrow.balanceOf(a0) == 0

    assert voting_escrow.getCurrentVotes(a1) == 0
    assert voting_escrow.getCurrentVotes(a0) == 0

    assert voting_escrow.getCurrentVotes(a1) == voting_escrow.balanceOf(a1)
    assert voting_escrow.getCurrentVotes(a0) == voting_escrow.balanceOf(a0)

    # Move to timing which is good for testing - beginning of a UTC week
    chain.sleep((chain[-1].timestamp // WEEK + 1) * WEEK - chain[-1].timestamp)
    chain.mine()

    chain.sleep(H)

    stages["before_deposits"] = (web3.eth.block_number, chain[-1].timestamp)

    voting_escrow.create_lock(amount, chain[-1].timestamp + WEEK, {"from": a0})
    stages["a0_deposit"] = (web3.eth.block_number, chain[-1].timestamp)

    chain.sleep(H)
    chain.mine()

    assert approx(voting_escrow.totalSupply(), amount // MAXTIME * (WEEK - 2 * H), TOL)
    assert approx(voting_escrow.balanceOf(a0), amount // MAXTIME * (WEEK - 2 * H), TOL)
    assert voting_escrow.balanceOf(a1) == 0
    t0 = chain[-1].timestamp

    stages["a0_in_0"] = []
    stages["a0_in_0"].append((web3.eth.block_number, chain[-1].timestamp))
    for i in range(7):
        for _ in range(24):
            chain.sleep(H)
            chain.mine()
        dt = chain[-1].timestamp - t0
        assert approx(
            voting_escrow.totalSupply(),
            amount // MAXTIME * max(WEEK - 2 * H - dt, 0),
            TOL,
        )
        assert approx(
            voting_escrow.balanceOf(a0),
            amount // MAXTIME * max(WEEK - 2 * H - dt, 0),
            TOL,
        )
        assert voting_escrow.balanceOf(a1) == 0
        stages["a0_in_0"].append((web3.eth.block_number, chain[-1].timestamp))

    chain.sleep(H)

    assert voting_escrow.balanceOf(a0) == 0
    voting_escrow.withdraw({"from": a0})
    stages["a0_withdraw"] = (web3.eth.block_number, chain[-1].timestamp)
    assert voting_escrow.totalSupply() == 0
    assert voting_escrow.balanceOf(a0) == 0
    assert voting_escrow.balanceOf(a1) == 0

    chain.sleep(H)
    chain.mine()

    # Next week (for round counting)
    chain.sleep((chain[-1].timestamp // WEEK + 1) * WEEK - chain[-1].timestamp)
    chain.mine()

    voting_escrow.create_lock(amount, chain[-1].timestamp + 2 * WEEK, {"from": a0})
    stages["a0_deposit_2"] = (web3.eth.block_number, chain[-1].timestamp)

    assert approx(voting_escrow.totalSupply(), amount // MAXTIME * 2 * WEEK, TOL)
    assert approx(voting_escrow.balanceOf(a0), amount // MAXTIME * 2 * WEEK, TOL)
    assert voting_escrow.balanceOf(a1) == 0

    voting_escrow.create_lock(amount, chain[-1].timestamp + WEEK, {"from": a1})
    stages["a1_deposit_2"] = (web3.eth.block_number, chain[-1].timestamp)

    assert approx(voting_escrow.totalSupply(), amount // MAXTIME * 3 * WEEK, TOL)
    assert approx(voting_escrow.balanceOf(a0), amount // MAXTIME * 2 * WEEK, TOL)
    assert approx(voting_escrow.balanceOf(a1), amount // MAXTIME * WEEK, TOL)

    t0 = chain[-1].timestamp
    chain.sleep(H)
    chain.mine()

    stages["a0_a1_in_2"] = []
    # Beginning of week: weight 3
    # End of week: weight 1
    for i in range(7):
        for _ in range(24):
            chain.sleep(H)
            chain.mine()
        dt = chain[-1].timestamp - t0
        w_total = voting_escrow.totalSupply()
        w_a0 = voting_escrow.balanceOf(a0)
        w_a1 = voting_escrow.balanceOf(a1)
        assert w_total == w_a0 + w_a1
        assert approx(w_a0, amount // MAXTIME * max(2 * WEEK - dt, 0), TOL)
        assert approx(w_a1, amount // MAXTIME * max(WEEK - dt, 0), TOL)
        stages["a0_a1_in_2"].append((web3.eth.block_number, chain[-1].timestamp))

    chain.sleep(H)
    chain.mine()

    voting_escrow.withdraw({"from": a1})
    t0 = chain[-1].timestamp
    stages["a1_withdraw_1"] = (web3.eth.block_number, chain[-1].timestamp)
    w_total = voting_escrow.totalSupply()
    w_a0 = voting_escrow.balanceOf(a0)
    assert w_a0 == w_total
    assert approx(w_total, amount // MAXTIME * (WEEK - 2 * H), TOL)
    assert voting_escrow.balanceOf(a1) == 0

    chain.sleep(H)
    chain.mine()

    stages["a0_in_2"] = []
    for i in range(7):
        for _ in range(24):
            chain.sleep(H)
            chain.mine()
        dt = chain[-1].timestamp - t0
        w_total = voting_escrow.totalSupply()
        w_a0 = voting_escrow.balanceOf(a0)
        assert w_total == w_a0
        assert approx(w_total, amount // MAXTIME * max(WEEK - dt - 2 * H, 0), TOL)
        assert voting_escrow.balanceOf(a1) == 0
        stages["a0_in_2"].append((web3.eth.block_number, chain[-1].timestamp))

    voting_escrow.withdraw({"from": a0})
    stages["a0_withdraw_2"] = (web3.eth.block_number, chain[-1].timestamp)

    chain.sleep(H)
    chain.mine()

    voting_escrow.withdraw({"from": a1})
    stages["a1_withdraw_2"] = (web3.eth.block_number, chain[-1].timestamp)

    assert voting_escrow.totalSupply() == 0
    assert voting_escrow.balanceOf(a0) == 0
    assert voting_escrow.balanceOf(a1) == 0

    # Now test historical balanceOfAt and others

    assert voting_escrow.balanceOfAt(a0, stages["before_deposits"][0]) == 0
    assert voting_escrow.balanceOfAt(a1, stages["before_deposits"][0]) == 0
    assert voting_escrow.totalSupplyAt(stages["before_deposits"][0]) == 0

    w_a0 = voting_escrow.balanceOfAt(a0, stages["a0_deposit"][0])
    assert approx(w_a0, amount // MAXTIME * (WEEK - H), TOL)
    assert voting_escrow.balanceOfAt(a1, stages["a0_deposit"][0]) == 0
    w_total = voting_escrow.totalSupplyAt(stages["a0_deposit"][0])
    assert w_a0 == w_total

    for i, (block, t) in enumerate(stages["a0_in_0"]):
        w_a0 = voting_escrow.balanceOfAt(a0, block)
        w_a1 = voting_escrow.balanceOfAt(a1, block)
        w_total = voting_escrow.totalSupplyAt(block)
        assert w_a1 == 0
        assert w_a0 == w_total
        time_left = WEEK * (7 - i) // 7 - 2 * H
        error_1h = H / time_left  # Rounding error of 1 block is possible, and we have 1h blocks
        assert approx(w_a0, amount // MAXTIME * time_left, error_1h)

    w_total = voting_escrow.totalSupplyAt(stages["a0_withdraw"][0])
    w_a0 = voting_escrow.balanceOfAt(a0, stages["a0_withdraw"][0])
    w_a1 = voting_escrow.balanceOfAt(a1, stages["a0_withdraw"][0])
    assert w_a0 == w_a1 == w_total == 0

    w_total = voting_escrow.totalSupplyAt(stages["a0_deposit_2"][0])
    w_a0 = voting_escrow.balanceOfAt(a0, stages["a0_deposit_2"][0])
    w_a1 = voting_escrow.balanceOfAt(a1, stages["a0_deposit_2"][0])
    assert approx(w_total, amount // MAXTIME * 2 * WEEK, TOL)
    assert w_total == w_a0
    assert w_a1 == 0

    w_total = voting_escrow.totalSupplyAt(stages["a1_deposit_2"][0])
    w_a0 = voting_escrow.balanceOfAt(a0, stages["a1_deposit_2"][0])
    w_a1 = voting_escrow.balanceOfAt(a1, stages["a1_deposit_2"][0])
    assert w_total == w_a0 + w_a1
    assert approx(w_total, amount // MAXTIME * 3 * WEEK, TOL)
    assert approx(w_a0, amount // MAXTIME * 2 * WEEK, TOL)

    t0 = stages["a1_deposit_2"][1]
    for i, (block, t) in enumerate(stages["a0_a1_in_2"]):
        w_a0 = voting_escrow.balanceOfAt(a0, block)
        w_a1 = voting_escrow.balanceOfAt(a1, block)
        w_total = voting_escrow.totalSupplyAt(block)
        assert w_total == w_a0 + w_a1
        dt = t - t0
        error_1h = H / (
            2 * WEEK - i * DAY
        )  # Rounding error of 1 block is possible, and we have 1h blocks
        assert approx(w_a0, amount // MAXTIME * max(2 * WEEK - dt, 0), error_1h)
        assert approx(w_a1, amount // MAXTIME * max(WEEK - dt, 0), error_1h)

    w_total = voting_escrow.totalSupplyAt(stages["a1_withdraw_1"][0])
    w_a0 = voting_escrow.balanceOfAt(a0, stages["a1_withdraw_1"][0])
    w_a1 = voting_escrow.balanceOfAt(a1, stages["a1_withdraw_1"][0])
    assert w_total == w_a0
    assert approx(w_total, amount // MAXTIME * (WEEK - 2 * H), TOL)
    assert w_a1 == 0

    t0 = stages["a1_withdraw_1"][1]
    for i, (block, t) in enumerate(stages["a0_in_2"]):
        w_a0 = voting_escrow.balanceOfAt(a0, block)
        w_a1 = voting_escrow.balanceOfAt(a1, block)
        w_total = voting_escrow.totalSupplyAt(block)
        assert w_total == w_a0
        assert w_a1 == 0
        dt = t - t0
        error_1h = H / (
            WEEK - i * DAY + DAY
        )  # Rounding error of 1 block is possible, and we have 1h blocks
        assert approx(w_total, amount // MAXTIME * max(WEEK - dt - 2 * H, 0), error_1h)

    w_total = voting_escrow.totalSupplyAt(stages["a1_withdraw_2"][0])
    w_a0 = voting_escrow.balanceOfAt(a0, stages["a1_withdraw_2"][0])
    w_a1 = voting_escrow.balanceOfAt(a1, stages["a1_withdraw_2"][0])
    assert w_total == w_a0 == w_a1 == 0
