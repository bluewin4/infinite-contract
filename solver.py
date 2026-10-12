"""Expectimax solver for the Infinite Contract Game.

Each turn the mover is dealt a random hand of `cards_per_turn` cards from
their deck and plays the best one. The value of a position for the mover is
therefore E[max over a random hand of the child values], which only needs the
value of every card in the deck: with the n child values sorted ascending,
card i (1-based) is the best in the hand with probability
C(i-1, k-1) / C(n, k).

Values are from Player 1's perspective: +1 Player 1 wins, -1 Player 2 wins,
0 for a draw or reaching the turn limit.
"""
from functools import lru_cache
from math import comb
from typing import Dict, List, Tuple

from main import create_game_config
from src.core.cards import Card

INITIAL_VARS = {'x': 1, 'y': 1, 'z': 1}

# A position is (code, order): the contract's lines and their execution order.
State = Tuple[Tuple[str, ...], Tuple[int, ...]]
EMPTY: State = ((), ())


def _compile(code: str):
    return compile(code, "<card>", "exec")


_COMPILED: Dict[str, object] = {}


def run_contract(state: State) -> Dict[str, int]:
    code, order = state
    env = dict(INITIAL_VARS)
    for idx in order:
        line = code[idx]
        if line not in _COMPILED:
            _COMPILED[line] = _compile(line)
        exec(_COMPILED[line], {"__builtins__": {}}, env)
    return env


def apply(state: State, card_code: str) -> State:
    """Mirror CodeContract.apply_card for the cards in the library"""
    code, order = state
    if card_code == "__contract__.pop()":
        if not code:
            return state
        last = len(code) - 1
        return code[:-1], tuple(i for i in order if i != last)
    if card_code == "__contract__.clear()":
        return EMPTY
    if card_code == "__contract__.invert()":
        return code, tuple(reversed(order))
    if card_code == "__contract__.optimize()":
        return code, tuple(range(len(code)))
    if card_code == "__contract__.clean()":
        return state  # every line is always in the execution order
    return code + (card_code,), order + (len(code),)


class Solver:
    def __init__(self, max_turns: int = 30, conditions=("x >= 3", "y >= 3")):
        config = create_game_config()
        self.hand_size = config.cards_per_turn
        self.decks: List[List[Card]] = []
        for target in ('x', 'y'):
            cards = []
            for card_type in config.get_allowed_cards(target):
                cards.extend(config.card_library.get_cards_by_type(card_type))
            self.decks.append(cards)
        self.max_turns = max_turns
        self.conditions = [self._parse(c) for c in conditions]
        self.value = lru_cache(maxsize=None)(self._value)

    @staticmethod
    def _parse(condition: str):
        var, target = condition.split('>=')
        return var.strip(), int(target)

    def outcome(self, state: State):
        """+1/-1/0 if the game is over in this position, else None"""
        env = run_contract(state)
        p1, p2 = (env[var] >= target for var, target in self.conditions)
        if p1 and p2:
            return 0
        if p1:
            return 1
        if p2:
            return -1
        return None

    def card_values(self, state: State, turns_left: int, mover: int) -> List[Tuple[float, Card]]:
        """Value (Player 1's perspective) of playing each card in the mover's deck"""
        results = []
        for card in self.decks[mover]:
            child = apply(state, card.code)
            result = self.outcome(child)
            if result is None:
                result = self.value(child, turns_left - 1, 1 - mover)
            results.append((result, card))
        return results

    def expected_best(self, values: List[float], mover: int) -> float:
        """E[best card in a random hand], from Player 1's perspective"""
        sign = 1 if mover == 0 else -1
        ordered = sorted(sign * v for v in values)
        n, k = len(ordered), self.hand_size
        total = sum(v * comb(i, k - 1) for i, v in enumerate(ordered))
        return sign * total / comb(n, k)

    def _value(self, state: State, turns_left: int, mover: int) -> float:
        if turns_left == 0:
            return 0.0
        values = [v for v, _ in self.card_values(state, turns_left, mover)]
        return self.expected_best(values, mover)

    def best_in_hand(self, state: State, turns_left: int, mover: int, hand: List[Card]):
        """Rank the cards in a specific hand, best first, with their values"""
        values = {c.id: v for v, c in self.card_values(state, turns_left, mover)}
        sign = 1 if mover == 0 else -1
        return sorted(((values[c.id], c) for c in hand), key=lambda vc: -sign * vc[0])


if __name__ == "__main__":
    import sys
    import time
    for horizon in range(1, int(sys.argv[1]) + 1 if len(sys.argv) > 1 else 7):
        solver = Solver(max_turns=horizon)
        start = time.time()
        v = solver.value(EMPTY, horizon, 0)
        info = solver.value.cache_info()
        print(f"horizon {horizon:2d}: value {v:+.4f}  "
              f"positions {info.currsize:>9,}  {time.time() - start:6.1f}s", flush=True)
