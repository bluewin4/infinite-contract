from src.core.game import InfiniteContractGame, GameConfig
from src.agents.base_agent import BaseAgent
from src.core.cards import CardLibrary, CardType
from src.agents.lm_agent import LMAgent
from src.agents.lm_config import LMConfig
import random
from typing import List

class SimpleAgent(BaseAgent):
    def __init__(self, name: str, victory_condition: str, target_var: str):
        super().__init__(name, victory_condition, target_var)

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
    
    def get_allowed_cards(target_var: str) -> List[CardType]:
        if target_var == 'x':
            return [
                CardType.AGGRESSIVE_X,    # Cards that help increase x
                CardType.DEFENSIVE_Y,     # Cards that hinder y's progress
                CardType.STRATEGIC,       # Strategic moves
                CardType.UTILITY          # Utility cards
            ]
        else:  # target_var == 'y'
            return [
                CardType.AGGRESSIVE_Y,    # Cards that help increase y
                CardType.DEFENSIVE_X,     # Cards that hinder x's progress
                CardType.STRATEGIC,       # Strategic moves
                CardType.UTILITY          # Utility cards
            ]
    
    return GameConfig(
        max_turns=25,
        memory_window=5,
        card_library=card_library,
        get_allowed_cards=get_allowed_cards,
        cards_per_turn=3
    )

def main():
    # Configurations for each agent
    agent1_config = {
        'target_var': 'x',
        'victory_condition': "x >= 3"
    }
    
    agent2_config = {
        'target_var': 'y',
        'victory_condition': "y >= 3"
    }
    
    # Create game configuration
    config = create_game_config()
    
    # Create LM agents
    agent1 = LMAgent(
        name="Player 1",
        model="claude-3-haiku-20240307",
        victory_condition=agent1_config['victory_condition'],
        temperature=0.7,
        max_tokens=500
    )
    
    agent2 = LMAgent(
        name="Player 2",
        model="claude-3-haiku-20240307",
        victory_condition=agent2_config['victory_condition'],
        temperature=0.8,
        max_tokens=500
    )
    
    # Alternatively, use SimpleAgent for testing
    # agent1 = SimpleAgent(
    #     name="Player 1",
    #     victory_condition=agent1_config['victory_condition'],
    #     target_var=agent1_config['target_var']
    # )
    
    # agent2 = SimpleAgent(
    #     name="Player 2",
    #     victory_condition=agent2_config['victory_condition'],
    #     target_var=agent2_config['target_var']
    # )
    
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

    # Add final game summary
    print("\n=== Game Summary ===")
    print(f"Total Turns: {game._game_result['total_turns']}")
    print(f"Final Variables: {game.contract.variables}")
    print(f"Winner: {game._game_result['winner'] or 'Draw'}")
    print(f"Victory Condition: {game._game_result['victory_condition']}")
    print("=" * 50)

if __name__ == "__main__":
    main() 