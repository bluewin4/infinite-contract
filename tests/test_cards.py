import pytest
from src.core.game import InfiniteContractGame, GameConfig
from src.core.cards import CardLibrary, CardType, Card
from src.agents.base_agent import BaseAgent

class TestAgent(BaseAgent):
    def __init__(self, name: str, victory_condition: str, fixed_card_number: int = 1):
        super().__init__(name)
        self.victory_condition = victory_condition
        self.fixed_card_number = fixed_card_number

    def get_response(self, prompt: str) -> str:
        return f"""
SCRATCH PAD:
Testing card {self.fixed_card_number}

SELECTED CARD: {self.fixed_card_number}
"""

def create_test_game(victory_condition: str = "x >= 5", 
                    agent1_card: int = 1, 
                    agent2_card: int = 1) -> InfiniteContractGame:
    config = GameConfig(
        max_turns=10,
        memory_window=5,
        card_library=CardLibrary(),
        allowed_card_types=[CardType.AGGRESSIVE, CardType.DEFENSIVE, 
                          CardType.STRATEGIC, CardType.UTILITY],
        cards_per_turn=3
    )
    
    agent1 = TestAgent("Player 1", victory_condition, agent1_card)
    agent2 = TestAgent("Player 2", victory_condition, agent2_card)
    
    return InfiniteContractGame(agent1, agent2, config)

def test_card_library_initialization():
    library = CardLibrary()
    # Test if all card types are present
    for card_type in CardType:
        cards = library.get_cards_by_type(card_type)
        assert len(cards) > 0, f"No cards found for type {card_type}"

@pytest.mark.parametrize("card_id,victory_condition,expected_vars", [
    # Basic operations on x
    ("op_increment_x", "x >= 10", {"x": 2, "y": 1, "z": 1}),  # 1 + 1 = 2
    ("op_decrement_x", "x >= 10", {"x": 0, "y": 1, "z": 1}),  # 1 - 1 = 0
    ("op_double_x", "x >= 10", {"x": 2, "y": 1, "z": 1}),     # 1 * 2 = 2
    ("op_halve_x", "x >= 10", {"x": 0, "y": 1, "z": 1}),      # 1 // 2 = 0
    
    # Transfer operations
    ("transfer_x_to_y", "x >= 10", {"x": 1, "y": 1, "z": 1}),
    ("transfer_y_to_x", "x >= 10", {"x": 1, "y": 1, "z": 1}),
    ("transfer_x_to_z", "x >= 10", {"x": 1, "y": 1, "z": 1}),
    ("transfer_z_to_x", "x >= 10", {"x": 1, "y": 1, "z": 1}),
    ("transfer_z_to_y", "x >= 10", {"x": 1, "y": 1, "z": 1}),
    
    # Utility operations
    ("util_reset_z", "x >= 10", {"x": 1, "y": 1, "z": 0}),  # Only z gets reset to 0
    ("op_abs_x", "x >= 10", {"x": 1, "y": 1, "z": 1}),  # abs(1) = 1
    ("op_abs_y", "x >= 10", {"x": 1, "y": 1, "z": 1}),  # abs(1) = 1
    ("op_abs_z", "x >= 10", {"x": 1, "y": 1, "z": 1}),  # abs(1) = 1
])
def test_individual_card_execution(card_id, victory_condition, expected_vars):
    library = CardLibrary()
    card = library.get_card(card_id)
    assert card is not None, f"Card {card_id} not found"
    
    # Create a game instance with initial state and victory condition
    game = create_test_game(victory_condition=victory_condition)
    
    # Apply the card
    game.contract.apply_card(card)
    
    # Check if variables match expected values
    for var, expected_value in expected_vars.items():
        assert game.contract.variables[var] == expected_value, \
            f"Card {card_id}: {var} expected {expected_value}, got {game.contract.variables[var]}"

def test_contract_manipulation_cards():
    game = create_test_game()
    library = CardLibrary()
    
    # Test pop operation
    increment_card = library.get_card("op_increment_x")
    pop_card = library.get_card("util_pop")
    
    game.contract.apply_card(increment_card)  # Add x += 1
    assert game.contract.variables["x"] == 2  # x starts at 1, then +1 = 2
    game.contract.apply_card(pop_card)  # Remove last line
    assert len(game.contract.current_code) == 0
    
    # Test clear operation
    clear_card = library.get_card("util_clear")
    game.contract.apply_card(increment_card)
    game.contract.apply_card(increment_card)
    assert len(game.contract.current_code) == 2
    game.contract.apply_card(clear_card)
    assert len(game.contract.current_code) == 0
    
    # Test invert operation
    invert_card = library.get_card("util_invert")
    transfer_card = library.get_card("transfer_x_to_y")
    
    game.contract.apply_card(increment_card)  # x += 1 (x becomes 2)
    game.contract.apply_card(transfer_card)   # y = x
    original_order = game.contract.execution_order.copy()
    game.contract.apply_card(invert_card)
    assert game.contract.execution_order != original_order
    
    # Verify the inversion actually changes execution behavior
    assert game.contract.variables["y"] == 1  # y should be 1 because x=1 when y=x is executed first

def test_card_availability():
    game = create_test_game(victory_condition="x >= 10")
    
    # Play multiple turns and verify that cards are being randomly selected
    seen_cards = set()
    for _ in range(10):
        prompt = game.create_turn_prompt()
        cards_section = prompt.split("Available Cards:")[1].split("Your Strategy Notes")[0]
        seen_cards.update(cards_section.strip().split('\n'))
    
    # Check if we've seen a good variety of cards
    assert len(seen_cards) > 5, "Not enough variety in card selection"

def test_card_categorization_by_goal():
    library = CardLibrary()
    
    # Test when goal is to increase x
    increment_x = library.get_card("op_increment_x")
    assert increment_x.card_type == CardType.AGGRESSIVE
    
    # Test utility cards are always utility
    clear_card = library.get_card("util_clear")
    assert clear_card.card_type == CardType.UTILITY
    
    # Test strategic cards are always strategic
    transfer_card = library.get_card("transfer_x_to_y")
    assert transfer_card.card_type == CardType.STRATEGIC

def test_victory_condition():
    # Test game with x >= 5 victory condition
    game = create_test_game(victory_condition="x >= 5")
    library = CardLibrary()
    
    # Get increment card
    increment_card = library.get_card("op_increment_x")
    
    # Apply card multiple times to exceed victory condition
    for _ in range(6):  # x will go from 1 to 7
        game.contract.apply_card(increment_card)
    
    # Check if victory condition is detected
    assert game.contract.check_victory_condition("x >= 5")
    
    # Test less than condition
    game = create_test_game(victory_condition="y <= -3")
    decrement_y = library.get_card("op_decrement_y")
    
    # Apply card multiple times to exceed victory condition
    for _ in range(4):  # y will go from 1 to -3
        game.contract.apply_card(decrement_y)
    
    assert game.contract.check_victory_condition("y <= -3")

def test_absolute_value_cards():
    library = CardLibrary()
    game = create_test_game(victory_condition="x >= 10")
    
    # Set up negative values
    game.contract.variables = {'x': -5, 'y': -3, 'z': -7}
    
    # Test abs(x)
    abs_x_card = library.get_card("op_abs_x")
    game.contract.apply_card(abs_x_card)
    assert game.contract.variables['x'] == 5
    
    # Test abs(y)
    abs_y_card = library.get_card("op_abs_y")
    game.contract.apply_card(abs_y_card)
    assert game.contract.variables['y'] == 3
    
    # Test abs(z)
    abs_z_card = library.get_card("op_abs_z")
    game.contract.apply_card(abs_z_card)
    assert game.contract.variables['z'] == 7