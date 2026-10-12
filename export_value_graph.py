"""Export the game's value graph: positions merged by their (x, y, z) values.

    python export_value_graph.py [--depth 3] [--games matches/g7 ...] [--out value_graph.json]
                                 [--html value_graph.html]

Explores every position within `depth` moves of the empty contract (not
expanding finished games), adds the positions reached in the given relay
games, and merges positions that produce the same (x, y, z). Each merged
node records how many positions it stands for, how close it is to the
start, whether it ends the game, and how often a single card from each
player's deck wins from it. Edges count the moves between merged nodes.
"""
import argparse
import json
import os
from collections import Counter, defaultdict

from main import TARGET
from solver import EMPTY, Solver, apply, run_contract
from src.core.cards import CardLibrary


def values(state):
    env = run_contract(state)
    return env['x'], env['y'], env['z']


def status(vals):
    p1, p2 = vals[0] >= TARGET, vals[1] >= TARGET
    return "draw" if p1 and p2 else "p1" if p1 else "p2" if p2 else None


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--games", nargs="*", default=[])
    parser.add_argument("--out", default="value_graph.json")
    parser.add_argument("--html", help="also write the interactive viewer with the data embedded")
    args = parser.parse_args()

    solver, library = Solver(max_turns=1), CardLibrary()
    decks = [[c.code for c in deck] for deck in solver.decks]
    all_codes = sorted(set(decks[0]) | set(decks[1]))
    ids_by_name = {c.name: c.id for c in library.cards.values()}

    # Positions near the start
    depth_of = {EMPTY: 0}
    frontier = [EMPTY]
    for depth in range(1, args.depth + 1):
        next_frontier = []
        for state in frontier:
            if status(values(state)):
                continue  # game over: don't expand
            for code in all_codes:
                child = apply(state, code)
                if child not in depth_of:
                    depth_of[child] = depth
                    next_frontier.append(child)
        frontier = next_frontier

    # Positions from real games
    games = []
    for path in args.games:
        with open(os.path.join(path, "result.json")) as f:
            result = json.load(f)
        state, route = EMPTY, [{"turn": 0, "player": None, "card": None, "vals": values(EMPTY)}]
        for t in result["transcript"]:
            if t["card"]:
                state = apply(state, library.get_card(ids_by_name[t["card"]]).code)
            depth_of.setdefault(state, None)
            route.append({"turn": t["turn"], "player": t["player"], "card": t["card"],
                          "vals": values(state)})
        games.append({"name": os.path.basename(path), "winner": result["winner"],
                      "turns": result["turns"], "route": route})

    # Merge by value
    nodes = defaultdict(lambda: {"positions": 0, "depth": None, "p1_wins_next": 0,
                                 "p2_wins_next": 0, "quiet_moves": 0})
    edges = defaultdict(Counter)  # (from_vals, to_vals) -> card name counts
    names_by_code = defaultdict(set)
    for card in library.cards.values():
        names_by_code[card.code].add(card.name)

    for state, depth in depth_of.items():
        vals = values(state)
        node = nodes[vals]
        node["positions"] += 1
        if depth is not None and (node["depth"] is None or depth < node["depth"]):
            node["depth"] = depth
        if status(vals):
            continue
        for mover, key in ((0, "p1_wins_next"), (1, "p2_wins_next")):
            if any(status(values(apply(state, code))) == ("p1", "p2")[mover] for code in decks[mover]):
                node[key] += 1
        for code in all_codes:
            child_vals = values(apply(state, code))
            if child_vals == vals:
                node["quiet_moves"] += 1
            elif depth is not None and depth < args.depth:
                for name in names_by_code[code]:
                    edges[(vals, child_vals)][name] += 1

    for game in games:  # make sure every step of a real game is an edge
        for a, b in zip(game["route"], game["route"][1:]):
            if a["vals"] != b["vals"]:
                edges[(tuple(a["vals"]), tuple(b["vals"]))][b["card"]] += 0
                nodes[tuple(b["vals"])]  # ensure node exists

    key = lambda v: f"{v[0]},{v[1]},{v[2]}"
    out = {
        "target": TARGET,
        "depth": args.depth,
        "positions_explored": len(depth_of),
        "nodes": [
            {"id": key(v), "x": v[0], "y": v[1], "z": v[2], "status": status(v),
             **{k: n[k] for k in ("positions", "depth", "quiet_moves")},
             "p1_threat": round(n["p1_wins_next"] / n["positions"], 3) if n["positions"] else 0,
             "p2_threat": round(n["p2_wins_next"] / n["positions"], 3) if n["positions"] else 0}
            for v, n in nodes.items()
        ],
        "edges": [
            {"source": key(a), "target": key(b), "count": sum(c.values()),
             "cards": [name for name, _ in c.most_common(4)]}
            for (a, b), c in edges.items() if a in nodes and b in nodes
        ],
        "games": [
            {**g, "route": [{**s, "vals": key(s["vals"])} for s in g["route"]]} for g in games
        ],
    }
    with open(args.out, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    if args.html:
        template = os.path.join(os.path.dirname(os.path.abspath(__file__)), "viewer", "value_graph.html")
        with open(template) as f:
            page = f.read()
        data = json.dumps(out, separators=(",", ":")).replace("</", "<\\/")
        with open(args.html, "w") as f:
            f.write(page.replace("/*DATA*/", data))
    print(f"{len(depth_of):,} positions -> {len(out['nodes'])} value nodes, "
          f"{len(out['edges'])} edges, {len(games)} games -> {args.out}")


if __name__ == "__main__":
    main()
