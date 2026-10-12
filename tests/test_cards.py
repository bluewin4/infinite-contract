import pytest
from src.core.game import InfiniteContractGame, GameConfig
from src.core.cards import CardLibrary, CardType, Card
from src.agents.base_agent import BaseAgent

class TestAgent(BaseAgent):
    __test__ = False  # not a pytest test class

    def __init__(self, name: str, victory_condition: str, fixed_card_number: int = 1,
                 target_var: str = "x"):
        super().__init__(name, victory_condition, target_var)
        self.fixed_card_number = fixed_card_number
        self.prompts = []

    def get_response(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return f"""
SCRATCH PAD:
Testing card {self.fixed_card_number}

SELECTED CARD: {self.fixed_card_number}
"""

def get_allowed_cards(target_var: str):
    if target_var == 'x':
        return [CardType.AGGRESSIVE_X, CardType.DEFENSIVE_Y, CardType.STRATEGIC, CardType.UTILITY]
    return [CardType.AGGRESSIVE_Y, CardType.DEFENSIVE_X, CardType.STRATEGIC, CardType.UTILITY]

def create_test_game(victory_condition: str = "x >= 5", 
                    agent1_card: int = 1, 
                    agent2_card: int = 1) -> InfiniteContractGame:
    config = GameConfig(
        max_turns=10,
        memory_window=5,
        card_library=CardLibrary(),
        get_allowed_cards=get_allowed_cards,
        cards_per_turn=3
    )
    
    agent1 = TestAgent("Player 1", victory_condition, agent1_card, target_var="x")
    agent2 = TestAgent("Player 2", victory_condition, agent2_card, target_var="y")
    
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
    assert increment_x.card_type == CardType.AGGRESSIVE_X
    
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

def test_transfer_cards_move_in_stated_direction():
    library = CardLibrary()
    game = create_test_game()
    game.contract.apply_card(library.get_card("op_double_x"))      # x = 2
    game.contract.apply_card(library.get_card("transfer_x_to_z"))  # z = 2
    game.contract.apply_card(library.get_card("util_reset_z"))     # z = 0
    game.contract.apply_card(library.get_card("transfer_z_to_x"))  # x = 0
    assert game.contract.variables == {"x": 0, "y": 1, "z": 0}

def test_clear_resets_variables():
    library = CardLibrary()
    game = create_test_game()
    for _ in range(3):
        game.contract.apply_card(library.get_card("op_increment_x"))
    game.contract.apply_card(library.get_card("util_clear"))
    assert game.contract.variables == {"x": 1, "y": 1, "z": 1}
    assert not game.contract.check_victory_condition("x >= 3")

def test_clean_preserves_execution_order():
    library = CardLibrary()
    game = create_test_game()
    game.contract.apply_card(library.get_card("op_increment_x"))   # x += 1
    game.contract.apply_card(library.get_card("transfer_x_to_y"))  # y = x
    game.contract.apply_card(library.get_card("util_invert"))
    assert game.contract.variables["y"] == 1
    game.contract.apply_card(library.get_card("util_clean"))
    assert game.contract.variables["y"] == 1
    # Adding a line re-runs the contract; y = x must still run before x += 1
    game.contract.apply_card(library.get_card("op_increment_x"))
    assert game.contract.variables == {"x": 3, "y": 1, "z": 1}

@pytest.mark.parametrize("card_number", [1, 2, 3])
def test_played_card_matches_shown_card(card_number):
    for _ in range(20):
        game = create_test_game(victory_condition="x >= 99", agent1_card=card_number)
        agent = game.agents['agent1']
        game.play_turn()
        cards_section = agent.prompts[-1].split("Available Cards:")[1].split("Your Strategy Notes")[0]
        shown = cards_section.strip().split('\n')[card_number - 1]
        played = game.history.turns[-1].card_name
        assert shown.startswith(f"{card_number}. {played}:")

def test_each_player_gets_cards_for_their_variable():
    game = create_test_game(victory_condition="x >= 99")
    library = CardLibrary()
    y_types = {CardType.AGGRESSIVE_Y, CardType.DEFENSIVE_X, CardType.STRATEGIC, CardType.UTILITY}
    game.current_player = 'agent2'
    for _ in range(20):
        game.create_turn_prompt()
        assert all(card.card_type in y_types for card in game.available_cards)

def test_lm_agent_keeps_target_var(monkeypatch):
    pytest.importorskip("litellm")
    from src.agents.lm_agent import LMAgent
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    agent = LMAgent("Player 2", model="claude-test", victory_condition="y >= 3", target_var="y")
    assert agent.target_var == "y"
    assert agent.victory_condition == "y >= 3"

@pytest.mark.parametrize("response,expected", [
    ("SELECTED CARD: 2", 2),
    ("SELECTED CARD: 3\n\nI chose this because...", 3),
    ("SELECTED CARD: [2]", 2),
    ("SELECTED CARD: 7", None),
    ("no selection here", None),
])
def test_extract_selected_card(response, expected):
    game = create_test_game()
    game.create_turn_prompt()
    assert game._extract_selected_card(response) == expected

def test_turn_records_strategy_notes_and_card_name():
    game = create_test_game(victory_condition="x >= 99")
    game.play_turn()
    assert game.agents['agent1'].strategy_notes == ["Testing card 1"]
    turn = game.history.turns[-1]
    assert turn.card_name is not None
    assert turn.player_name == "Player 1"
    assert turn.card_name in game._format_history([turn])

def test_both_conditions_met_is_a_draw():
    game = create_test_game(victory_condition="x >= 99")
    game.agents['agent1'].victory_condition = "x >= 1"
    game.agents['agent2'].victory_condition = "y >= 1"
    assert game.play_turn() is False
    assert game.winner == "draw"

def test_single_winner_is_recorded():
    game = create_test_game(victory_condition="x >= 99")
    game.agents['agent2'].victory_condition = "y >= 1"
    assert game.play_turn() is False
    assert game.winner == "Player 2"

def test_turn_timestamps_are_per_turn():
    from src.core.history import TurnRecord
    first = TurnRecord(1, "a", "", 1, [], {})
    import time; time.sleep(0.01)
    second = TurnRecord(2, "a", "", 1, [], {})
    assert first.timestamp < second.timestamp

def test_lm_agent_omits_temperature_by_default(monkeypatch):
    pytest.importorskip("litellm")
    from src.agents import lm_agent
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    calls = []
    class Msg: content = "SELECTED CARD: 1"
    class Choice: message = Msg()
    class Resp: choices = [Choice()]
    monkeypatch.setattr(lm_agent, "completion", lambda **kw: calls.append(kw) or Resp())
    lm_agent.LMAgent("P1", model="claude-haiku-5-5", victory_condition="x >= 3").get_response("hi")
    lm_agent.LMAgent("P1", model="claude-haiku-5-5", victory_condition="x >= 3",
                     temperature=0.5, top_k=5).get_response("hi")
    assert "temperature" not in calls[0]
    assert calls[1]["temperature"] == 0.5 and calls[1]["top_k"] == 5
