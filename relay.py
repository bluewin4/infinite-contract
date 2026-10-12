"""File-based relay so external players (e.g. Claude Code subagents) can play.

Start a game server, then have each player loop on `turn` / `respond`:

    python relay.py serve   --dir matches/g1 [--max-turns 40]
    python relay.py turn    --dir matches/g1 --player 1   # blocks, prints prompt
    python relay.py respond --dir matches/g1 --player 1 < response.txt

`turn` prints "GAME OVER" and the result once the game has ended.
"""
import argparse
import json
import os
import sys
import time
from types import SimpleNamespace

from main import VICTORY_CONDITIONS, create_game_config
from src.agents.base_agent import BaseAgent
from src.agents.lm_agent import LMAgent
from src.core.game import InfiniteContractGame

PLAYERS = {
    1: {"name": "Player 1", "victory_condition": VICTORY_CONDITIONS['x'], "target_var": "x"},
    2: {"name": "Player 2", "victory_condition": VICTORY_CONDITIONS['y'], "target_var": "y"},
}
POLL_SECONDS = 0.5


def _path(match_dir: str, player: int, kind: str) -> str:
    return os.path.join(match_dir, f"p{player}_{kind}.txt")


def _write_atomic(path: str, text: str):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(text)
    os.replace(tmp, path)


class RelayAgent(BaseAgent):
    """Agent whose moves come from files written by an external player"""

    def __init__(self, player: int, match_dir: str, timeout: float):
        super().__init__(**PLAYERS[player])
        self.player = player
        self.match_dir = match_dir
        self.timeout = timeout

    def get_response(self, prompt: str) -> str:
        response_path = _path(self.match_dir, self.player, "response")
        _write_atomic(_path(self.match_dir, self.player, "prompt"), prompt)
        deadline = time.time() + self.timeout
        while not os.path.exists(response_path):
            if time.time() > deadline:
                return "TIMEOUT"  # counts as an invalid move
            time.sleep(POLL_SECONDS)
        with open(response_path) as f:
            response = f.read()
        os.remove(response_path)
        return response


def rules_text(player: int) -> str:
    info = PLAYERS[player]
    return LMAgent._create_system_prompt(
        SimpleNamespace(name=info["name"], victory_condition=info["victory_condition"]))


def serve(args):
    os.makedirs(args.dir, exist_ok=True)
    agents = [RelayAgent(p, args.dir, args.turn_timeout) for p in (1, 2)]
    game = InfiniteContractGame(agents[0], agents[1], create_game_config())

    for _ in range(args.max_turns):
        if not game.play_turn():
            break

    turns = game.history.turns
    result = {
        "winner": game.winner or "no winner",
        "turns": len(turns),
        "final_variables": game.contract.variables,
        "final_contract": game.contract.current_code,
        "transcript": [
            {"turn": t.turn_number, "player": t.player_name, "card": t.card_name,
             "hand": t.hand, "variables": t.variables, "response": t.thought_process}
            for t in turns
        ],
    }
    _write_atomic(os.path.join(args.dir, "result.json"), json.dumps(result, indent=2))
    print(f"{result['winner']} after {result['turns']} turns - {result['final_variables']}")


def turn(args):
    prompt_path = _path(args.dir, args.player, "prompt")
    result_path = os.path.join(args.dir, "result.json")
    while True:
        if os.path.exists(prompt_path):
            with open(prompt_path) as f:
                print(f.read())
            return
        if os.path.exists(result_path):
            with open(result_path) as f:
                result = json.load(f)
            print(f"GAME OVER: {result['winner']} after {result['turns']} turns. "
                  f"Final variables: {result['final_variables']}")
            return
        time.sleep(POLL_SECONDS)


def respond(args):
    prompt_path = _path(args.dir, args.player, "prompt")
    if not os.path.exists(prompt_path):
        sys.exit("It is not your turn - run `turn` first.")
    os.remove(prompt_path)
    _write_atomic(_path(args.dir, args.player, "response"), sys.stdin.read())
    print("Move submitted.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("serve")
    p.add_argument("--dir", required=True)
    p.add_argument("--max-turns", type=int, default=40)
    p.add_argument("--turn-timeout", type=float, default=600)
    p.set_defaults(func=serve)

    for name, func in (("turn", turn), ("respond", respond)):
        p = sub.add_parser(name)
        p.add_argument("--dir", required=True)
        p.add_argument("--player", type=int, choices=(1, 2), required=True)
        p.set_defaults(func=func)

    p = sub.add_parser("rules")
    p.add_argument("--player", type=int, choices=(1, 2), required=True)
    p.set_defaults(func=lambda a: print(rules_text(a.player)))

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
