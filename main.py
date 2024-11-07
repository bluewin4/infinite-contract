from src.core.game import InfiniteContractGame, GameConfig
from src.agents.base_agent import BaseAgent
from src.core.cards import CardLibrary, CardType
from src.agents.lm_agent import LMAgent
from src.agents.lm_config import LMConfig
import random

class SimpleAgent(BaseAgent):
    def get_response(self, prompt: str) -> str:
        # Extract available cards from prompt
        cards_section = prompt.split("Available Cards:")[1].split("Your Strategy Notes")[0]
        num_cards = len(cards_section.strip().split('\n'))
        
        # Choose a random card from available ones
        selected_card = random.randint(1, num_cards)
        
        return f"""
SCRATCH PAD:
Analyzing available cards...
Choosing card {selected_card} randomly.

SELECTED CARD: {selected_card}
"""

def create_game_config() -> GameConfig:
    card_library = CardLibrary()
    
    return GameConfig(
        max_turns=50,
        memory_window=5,
        card_library=card_library,
        allowed_card_types=[
            CardType.AGGRESSIVE, 
            CardType.DEFENSIVE, 
            CardType.STRATEGIC,
            CardType.UTILITY
        ],
        cards_per_turn=3
    )

def main():
    # Define victory conditions
    agent1_goal = "x >= 10"
    
    # Create game configuration
    config = create_game_config()
    
    # Create agents with explicit goals
    agent1 = LMAgent(
        name="Player 1",
        model="claude-3-haiku-20240307",
        victory_condition=agent1_goal,
        temperature=0.7,
        max_tokens=500
    )
    
    agent2 = LMAgent(
        name="Player 2",
        model="claude-3-haiku-20240307",
        victory_condition=agent1_goal,
        temperature=0.8,
        max_tokens=500
    )
    
    # Create and run game
    game = InfiniteContractGame(agent1, agent2, config)
    run_game_with_logging(game, config.max_turns)

def run_game_with_logging(game: InfiniteContractGame, max_turns: int):
    turn_count = 0
    while game.play_turn() and turn_count < max_turns:
        turn_count += 1
        current_turn = game.history.get_turn(turn_count)
        
        print(f"\n=== Turn {turn_count} ===")
        print(f"Player: {current_turn.player_name}")
        print(f"Thought Process:\n{current_turn.thought_process}")
        print(f"Contract:\n{current_turn.contract_state}")
        print(f"Variables: {current_turn.variables}")
        print("-" * 50)

if __name__ == "__main__":
    main() 