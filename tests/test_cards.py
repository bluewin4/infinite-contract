import pytest
from src.core.cards import CardLibrary, CardType, Card
from src.core.game import InfiniteContractGame, GameConfig
from src.core.contract import CodeContract
from src.agents.base_agent import BaseAgent

class TestAgent(BaseAgent):
    def __init__(self, name: str, victory_condition: str, target_var: str, card_to_play: int):
        super().__init__(name, victory_condition, target_var)
        self.card_to_play = card_to_play
        
    def get_response(self, prompt: str) -> str:
        return f"""
SCRATCH PAD:
Testing card {self.card_to_play}

SELECTED CARD: {self.card_to_play}
"""

def create_test_game(victory_condition: str = "x >= 5",
                    agent1_card: int = 1,
                    agent2_card: int = 1) -> InfiniteContractGame:
    config = GameConfig(
        max_turns=10,
        memory_window=5,
        card_library=CardLibrary(),
        get_allowed_cards=lambda target_var: [
            CardType.AGGRESSIVE_X if target_var == 'x' else CardType.AGGRESSIVE_Y,
            CardType.DEFENSIVE_X if target_var == 'y' else CardType.DEFENSIVE_Y,
            CardType.STRATEGIC,
            CardType.UTILITY
        ],
        cards_per_turn=3
    )

    agent1 = TestAgent("Player 1", victory_condition, "x", agent1_card)
    agent2 = TestAgent("Player 2", victory_condition, "y", agent2_card)
    
    return InfiniteContractGame(agent1, agent2, config)

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
    assert game.contract.variables == expected_vars, \
        f"Expected {expected_vars}, got {game.contract.variables}"

def test_contract_manipulation_cards():
    game = create_test_game()
    library = CardLibrary()
    
    # Test clear contract
    clear_card = library.get_card("util_clear")
    game.contract.apply_card(clear_card)
    assert len(game.contract.current_code) == 0
    
    # Add some lines and test pop
    increment_card = library.get_card("op_increment_x")
    game.contract.apply_card(increment_card)
    game.contract.apply_card(increment_card)
    
    pop_card = library.get_card("util_pop")
    game.contract.apply_card(pop_card)
    assert len(game.contract.current_code) == 1

def test_card_availability():
    game = create_test_game(victory_condition="x >= 10")
    
    # Get available cards for current player
    available_cards = game._get_available_cards()
    
    # Check that we got the right number of cards
    assert len(available_cards) == game.config.cards_per_turn
    
    # Check that all cards are valid
    for card in available_cards:
        assert isinstance(card, Card)

def test_card_categorization_by_goal():
    library = CardLibrary()

    # Test when goal is to increase x
    increment_x = library.get_card("op_increment_x")
    assert increment_x.card_type == CardType.AGGRESSIVE_X
    
    # Test when goal is to increase y
    increment_y = library.get_card("op_increment_y")
    assert increment_y.card_type == CardType.AGGRESSIVE_Y

def test_victory_condition():
    # Test game with x >= 5 victory condition
    game = create_test_game(victory_condition="x >= 5")
    
    # Apply cards to reach victory condition
    library = CardLibrary()
    double_x = library.get_card("op_double_x")
    increment_x = library.get_card("op_increment_x")
    
    # Double x (1 -> 2) and increment three times (2 -> 5)
    game.contract.apply_card(double_x)
    for _ in range(3):
        game.contract.apply_card(increment_x)
    
    # Check victory condition
    assert game.contract.check_victory_condition("x >= 5")

@pytest.mark.parametrize("cards,expected_vars", [
    # Test multiple cards in sequence
    (["op_increment_x", "op_increment_x"], {"x": 3, "y": 1, "z": 1}),  # 1->2->3
    (["op_double_x", "op_increment_x"], {"x": 3, "y": 1, "z": 1}),     # 1->2->3
    (["op_increment_y", "op_double_y"], {"x": 1, "y": 4, "z": 1}),     # 1->2->4
])
def test_multiple_card_execution(cards, expected_vars):
    library = CardLibrary()
    game = create_test_game()
    
    # Apply sequence of cards
    for card_id in cards:
        card = library.get_card(card_id)
        game.contract.apply_card(card)
        game.contract._execute_contract()  # Changed from execute_contract to _execute_contract
    
    assert game.contract.variables == expected_vars, \
        f"Expected {expected_vars}, got {game.contract.variables}"

def test_contract_manipulation():
    contract = CodeContract()
    
    # Test clear contract
    # First add some lines
    contract.add_line("x = x + 1")
    contract.add_line("y = y + 1")
    assert len(contract.current_code) == 2
    
    # Test clear
    contract.apply_card(Card(
        id="util_clear",
        name="Clear Contract",
        description="Remove all lines from the contract",
        code="__contract__.clear()",
        card_type=CardType.UTILITY,
        complexity=3
    ))
    assert len(contract.current_code) == 0
    assert len(contract.execution_order) == 0
    assert contract.variables == {'x': 1, 'y': 1, 'z': 1}  # Should reset to initial state

    # Test invert contract
    contract.add_line("x = x + 1")  # x becomes 2
    contract.add_line("x = x * 2")  # x becomes 4
    assert contract.variables['x'] == 4
    
    contract.apply_card(Card(
        id="util_invert",
        name="Invert Execution",
        description="Reverse the order of contract execution",
        code="__contract__.invert()",
        card_type=CardType.UTILITY,
        complexity=3
    ))
    # After inversion:
    # 1. x = x * 2 (x: 1 -> 2)
    # 2. x = x + 1 (x: 2 -> 3)
    assert contract.variables['x'] == 3
    assert contract.execution_order == [1, 0]  # Order should be reversed

def test_invert_with_complex_operations():
    contract = CodeContract()
    
    # Add sequence of operations
    contract.add_line("x = x + 1")  # x: 1 -> 2
    contract.add_line("y = x")      # y: 1 -> 2
    contract.add_line("x = x * 2")  # x: 2 -> 4
    
    # Test normal execution
    assert contract.variables == {'x': 4, 'y': 2, 'z': 1}
    
    # Test inverted execution
    contract.apply_card(Card(
        id="util_invert",
        name="Invert Execution",
        description="Reverse the order of contract execution",
        code="__contract__.invert()",
        card_type=CardType.UTILITY,
        complexity=3
    ))
    # After inversion:
    # 1. x = x * 2  (x: 1 -> 2)
    # 2. y = x      (y: 1 -> 2)
    # 3. x = x + 1  (x: 2 -> 3)
    assert contract.variables == {'x': 3, 'y': 2, 'z': 1}