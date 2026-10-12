"""Score each move in finished relay games against the solver.

    python score_moves.py matches/g7 matches/g8 [--depth 3]

For every turn, the position is rebuilt and the solver values each card in
the hand that was dealt, looking `depth` turns ahead. A move's regret is the
value of the best card in the hand minus the value of the card played, from
the mover's side (0 = best available move). Moves where every card in the
hand had the same value are "forced" and say nothing about skill, so the
summary counts only "decisive" moves. The random baseline is the regret of
picking a card uniformly from the same hand.
"""
import argparse
import json
import os
from collections import defaultdict

from solver import EMPTY, Solver, apply
from src.core.cards import CardLibrary

MAX_TURNS = 30
EPS = 1e-9


def score_game(solver: Solver, library: CardLibrary, path: str, depth: int):
    with open(os.path.join(path, "result.json")) as f:
        result = json.load(f)
    ids_by_name = {c.name: c.id for c in library.cards.values()}

    state, moves = EMPTY, []
    for t in result["transcript"]:
        mover = 0 if t["player"] == "Player 1" else 1
        sign = 1 if mover == 0 else -1
        turns_left = min(depth, MAX_TURNS - t["turn"] + 1)
        hand = [library.get_card(cid) for cid in t["hand"]]
        values = {c.id: sign * v for v, c in solver.best_in_hand(state, turns_left, mover, hand)}
        best = max(values.values())
        played = ids_by_name.get(t["card"]) if t["card"] else None
        move = {
            "game": os.path.basename(path), "turn": t["turn"], "player": t["player"],
            "card": t["card"], "decisive": max(values.values()) - min(values.values()) > EPS,
            "random_regret": sum(best - v for v in values.values()) / len(values),
        }
        if played is None:
            move.update(regret=best - min(values.values()), best=False)  # skipped turn
        else:
            move.update(regret=best - values[played], best=values[played] >= best - EPS)
            state = apply(state, library.get_card(played).code)
        moves.append(move)
    return result, moves


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("games", nargs="+")
    parser.add_argument("--depth", type=int, default=3)
    args = parser.parse_args()

    solver, library = Solver(max_turns=args.depth), CardLibrary()
    totals = defaultdict(lambda: defaultdict(float))
    for path in args.games:
        result, moves = score_game(solver, library, path, args.depth)
        print(f"\n{os.path.basename(path)}: {result['winner']} after {result['turns']} turns")
        for m in moves:
            if m["decisive"] and not m["best"]:
                print(f"  turn {m['turn']:>2} {m['player']}: played {m['card'] or 'nothing'}"
                      f" - regret {m['regret']:.2f} (random {m['random_regret']:.2f})")
        for m in moves:
            row = totals[m["player"]]
            row["moves"] += 1
            if m["decisive"]:
                row["decisive"] += 1
                row["best"] += m["best"]
                row["regret"] += m["regret"]
                row["random_regret"] += m["random_regret"]

    print(f"\n=== Move quality vs solver ({args.depth} turns ahead), decisive moves only ===")
    for player in sorted(totals):
        r = totals[player]
        d = r["decisive"] or 1
        print(f"{player}: {int(r['decisive'])} decisive of {int(r['moves'])} moves - "
              f"best move {100 * r['best'] / d:.0f}%, mean regret {r['regret'] / d:.3f} "
              f"(random play {r['random_regret'] / d:.3f})")


if __name__ == "__main__":
    main()
