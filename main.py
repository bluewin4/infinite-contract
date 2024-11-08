from src.core.game import InfiniteContractGame, GameConfig
from src.agents.base_agent import BaseAgent
from src.core.cards import CardLibrary, CardType
from src.agents.lm_agent import LMAgent
import random
from src.core.analytics import GameAnalytics

class SimpleAgent(BaseAgent):
    def __init__(self, name: str, victory_condition: str):
        super().__init__(name)
        self.victory_condition = victory_condition
        self.model = "simple"

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
    # Create analytics instance
    analytics = GameAnalytics(storage_path="game_data")
    
    # Define victory conditions
    agent1_goal = "x >= 10"
    
    # Create game configuration
    config = create_game_config()
    
    # Create agents with explicit goals
    # agent1 = LMAgent(
    #     name="Player 1",
    #     model="claude-3-haiku-20240307",
    #     victory_condition=agent1_goal,
    #     temperature=0.7,
    #     max_tokens=500
    # )
    
    # agent2 = LMAgent(
    #     name="Player 2",
    #     model="claude-3-haiku-20240307",
    #     victory_condition=agent1_goal,
    #     temperature=0.8,
    #     max_tokens=500
    # )

    agent1 = SimpleAgent(
        name="Player 1",
        victory_condition=agent1_goal
    )
    
    agent2 = SimpleAgent(
        name="Player 2", 
        victory_condition=agent1_goal
    )
    
    # Create and run game
    game = InfiniteContractGame(agent1, agent2, config)
    game.analytics = analytics  # Set analytics explicitly
    run_game_with_logging(game, config.max_turns)

def run_game_with_logging(game: InfiniteContractGame, max_turns: int):
    while game.turn_count < max_turns and game.play_turn():
        current_turn = game.history.turns[-1]
        
        print(f"\n=== Turn {current_turn.turn_number} ===")
        print(f"Player: {current_turn.player_name}")
        print(f"Thought Process:\n{current_turn.thought_process}")
        print(f"Contract:\n{current_turn.contract_state}")
        print(f"Variables: {current_turn.variables}")
        print("-" * 50)

if __name__ == "__main__":
    main() 