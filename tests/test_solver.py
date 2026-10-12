import random

from solver import EMPTY, Solver, apply, run_contract
from src.core.cards import CardLibrary
from src.core.contract import CodeContract


def test_solver_rules_match_engine():
    cards = list(CardLibrary().cards.values())
    for seed in range(300):
        rng = random.Random(seed)
        contract, state = CodeContract(), EMPTY
        for _ in range(rng.randint(1, 25)):
            card = rng.choice(cards)
            contract.apply_card(card)
            state = apply(state, card.code)
            assert (tuple(contract.current_code), tuple(contract.execution_order)) == state
            assert contract.variables == run_contract(state)


def test_expected_best_matches_enumeration():
    from itertools import combinations
    solver = Solver(max_turns=1)
    values = [0.3, -1.0, 0.5, 0.0, 1.0, -0.2]
    for mover, pick in ((0, max), (1, min)):
        hands = list(combinations(values, solver.hand_size))
        brute = sum(pick(h) for h in hands) / len(hands)
        assert abs(solver.expected_best(values, mover) - brute) < 1e-12


def test_solver_finds_immediate_win():
    solver = Solver(max_turns=3)
    library = CardLibrary()
    state = apply(EMPTY, "x += 1")  # x = 2: Increment X or Double X wins now
    hand = [library.get_card("util_reset_z"), library.get_card("op_double_x"),
            library.get_card("transfer_x_to_z")]
    ranked = solver.best_in_hand(state, 3, 0, hand)
    assert ranked[0][1].id == "op_double_x" and ranked[0][0] == 1
