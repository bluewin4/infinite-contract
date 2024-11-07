from src.core.game import InfiniteContractGame, GameConfig
from src.agents.base_agent import BaseAgent
from src.core.cards import CardLibrary, CardType
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

def main():
    # Add debug printing
    card_library = CardLibrary()
    print("Available cards in library:")
    for card_type in [CardType.AGGRESSIVE, CardType.DEFENSIVE, CardType.STRATEGIC]:
        print(f"\n{card_type.value} cards:")
        for card in card_library.get_cards_by_type(card_type):
            print(f"- {card.name}: {card.code}")
    
    # Initialize card library
    card_library = CardLibrary()
    
    # Create game configuration
    config = GameConfig(
        max_turns=50,
        memory_window=5,
        victory_conditions={
            'agent1': 'x >= 10',
            'agent2': 'y <= -5'
        },
        card_library=card_library,
        allowed_card_types=[
            CardType.AGGRESSIVE, 
            CardType.DEFENSIVE, 
            CardType.STRATEGIC,
            CardType.UTILITY
        ],
        cards_per_turn=3
    )
    
    # Create agents
    agent1 = SimpleAgent("Player 1")
    agent2 = SimpleAgent("Player 2")
    
    # Create and run game
    game = InfiniteContractGame(agent1, agent2, config)
    
    # Play until game over
    turn_count = 0
    while game.play_turn() and turn_count < config.max_turns:
        turn_count += 1
        print(f"\nTurn {turn_count}:")
        print(f"Player: {game.current_player}")
        print(f"Contract:\n{game.contract.current_code}")
        print(f"Variables: {game.contract.variables}")
    
    print("\nGame Over!")
    print(f"Final variables: {game.contract.variables}")
    print(f"Total turns: {turn_count}")

if __name__ == "__main__":
    main() 