"""Play a batch of LM-vs-LM games and summarise the results.

Usage:
    python run_matches.py --games 10 --model claude-haiku-5-5

Each game's full transcript is written to logs/<timestamp>/game_<n>.json.
"""
import argparse
import contextlib
import io
import json
import os
from collections import Counter
from datetime import datetime

from main import VICTORY_CONDITIONS, create_game_config
from src.agents.lm_agent import LMAgent
from src.core.game import InfiniteContractGame


def play_game(model: str, max_turns: int, max_tokens: int) -> dict:
    agents = [
        LMAgent(name="Player 1", model=model, victory_condition=VICTORY_CONDITIONS['x'],
                target_var="x", max_tokens=max_tokens),
        LMAgent(name="Player 2", model=model, victory_condition=VICTORY_CONDITIONS['y'],
                target_var="y", max_tokens=max_tokens),
    ]
    game = InfiniteContractGame(agents[0], agents[1], create_game_config())

    error = None
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            for _ in range(max_turns):
                if not game.play_turn():
                    break
        except RuntimeError as e:  # LLM call failed; keep the partial game
            error = str(e)

    turns = game.history.turns
    return {
        "winner": game.winner or ("error" if error else "no winner"),
        "turns": len(turns),
        "invalid_moves": Counter(t.player_name for t in turns if t.card_name is None),
        "cards_played": Counter(t.card_name for t in turns if t.card_name),
        "final_variables": game.contract.variables,
        "final_contract": game.contract.current_code,
        "error": error,
        "transcript": [
            {
                "turn": t.turn_number,
                "player": t.player_name,
                "card": t.card_name,
                "variables": t.variables,
                "contract": t.contract_state,
                "response": t.thought_process,
            }
            for t in turns
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--model", default="claude-haiku-5-5")
    parser.add_argument("--max-turns", type=int, default=50)
    parser.add_argument("--max-tokens", type=int, default=4096)
    args = parser.parse_args()

    log_dir = os.path.join("logs", datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(log_dir, exist_ok=True)

    results = []
    for n in range(1, args.games + 1):
        result = play_game(args.model, args.max_turns, args.max_tokens)
        results.append(result)
        with open(os.path.join(log_dir, f"game_{n}.json"), "w") as f:
            json.dump(result, f, indent=2)
        invalid = sum(result["invalid_moves"].values())
        print(f"Game {n}: {result['winner']} in {result['turns']} turns "
              f"({invalid} invalid moves) - final {result['final_variables']}"
              + (f" - ERROR: {result['error']}" if result["error"] else ""))

    total_turns = sum(r["turns"] for r in results)
    invalid = sum((r["invalid_moves"] for r in results), Counter())
    cards = sum((r["cards_played"] for r in results), Counter())
    print(f"\n=== {args.games} games, model {args.model} ===")
    print("Results:", dict(Counter(r["winner"] for r in results)))
    print(f"Average length: {total_turns / len(results):.1f} turns")
    print(f"Invalid moves: {dict(invalid)} of {total_turns} turns")
    print("Most played cards:", cards.most_common(5))
    print(f"Transcripts: {log_dir}/")


if __name__ == "__main__":
    main()
