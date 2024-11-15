from src.agents.lm_agent import LMAgent
from src.core.game import InfiniteContractGame, GameConfig
from src.core.cards import CardLibrary, CardType
import pytest
import os
import json
from datetime import datetime
from unittest.mock import patch

# Mock response for LiteLLM completion
MOCK_RESPONSE = type('MockResponse', (), {
    'choices': [
        type('MockChoice', (), {
            'message': type('MockMessage', (), {
                'content': """
SCRATCH PAD:
Looking at current state:
x = 1, y = 1
Need to increase x to win
Card 1 looks like the best option as it directly increases x

SELECTED CARD: Card 1
"""
            }),
            'role': 'assistant'
        })
    ],
    'model': 'claude-3-haiku-20240307'
})

def create_test_game_config() -> GameConfig:
    """Reference to existing game config creation"""
    card_library = CardLibrary()
    
    def get_allowed_cards(target_var: str):
        return [CardType.AGGRESSIVE_X, CardType.DEFENSIVE_Y, CardType.STRATEGIC, CardType.UTILITY]
    
    return GameConfig(
        max_turns=5,
        memory_window=3,
        card_library=card_library,
        get_allowed_cards=get_allowed_cards,
        cards_per_turn=3
    )

@pytest.fixture
def setup_test_environment(tmp_path):
    # Create a temporary directory for test storage
    test_storage = tmp_path / "test_storage"
    test_storage.mkdir()
    
    # Set environment variables for testing
    os.environ["STORAGE_PATH"] = str(test_storage)
    
    # Create profiles.json with initial empty structure
    profiles_path = test_storage / "profiles.json"
    with open(profiles_path, 'w') as f:
        json.dump({}, f)
    
    return test_storage

@pytest.fixture
def test_lm_agent():
    def _create_agent(name: str, victory_condition: str):
        return LMAgent(
            name=name,
            model="claude-3-haiku-20240307",
            victory_condition=victory_condition,
            temperature=0.7,
            max_tokens=500,
            testing=True
        )
    return _create_agent

@patch('litellm.completion')
def test_lm_agent_profile_creation(mock_completion, setup_test_environment, test_lm_agent):
    # Configure mock
    mock_completion.return_value = MOCK_RESPONSE
    
    config = create_test_game_config()
    
    # Create agents using the fixture
    agent1 = test_lm_agent("Test Player 1", "x >= 3")
    agent2 = test_lm_agent("Test Player 2", "y >= 3")
    
    # Create and run game
    game = InfiniteContractGame(agent1, agent2, config)
    
    # Play a few turns
    for _ in range(3):
        if not game.play_turn():
            break
    
    # Verify profiles were created and updated correctly
    profiles_path = setup_test_environment / "profiles.json"
    assert profiles_path.exists()
    
    with open(profiles_path) as f:
        profiles = json.load(f)
    
    # Check for both agents
    agent1_id = f"{agent1.name}_lmagent"
    agent2_id = f"{agent2.name}_lmagent"
    
    assert agent1_id in profiles
    assert agent2_id in profiles
    
    # Verify profile structure
    for agent_id in [agent1_id, agent2_id]:
        profile = profiles[agent_id]
        assert "name" in profile
        assert "model_type" in profile
        assert "model_params" in profile
        assert "stats" in profile
        assert "game_history" in profile
        
        # Check stats structure
        assert "total_games" in profile["stats"]
        assert "games_won" in profile["stats"]
        assert "avg_turns_to_win" in profile["stats"]
        assert "favorite_card_types" in profile["stats"]
        assert "victory_conditions" in profile["stats"]

@patch('litellm.completion')
def test_profile_updates_after_game(mock_completion, setup_test_environment, test_lm_agent):
    # Configure mock
    mock_completion.return_value = MOCK_RESPONSE
    
    config = create_test_game_config()
    
    # Create agents using the fixture
    agent1 = test_lm_agent("Test Player 1", "x >= 3")
    agent2 = test_lm_agent("Test Player 2", "y >= 3")
    
    # Run multiple games
    for _ in range(2):
        game = InfiniteContractGame(agent1, agent2, config)
        while game.play_turn():
            pass
    
    # Verify profile updates
    profiles_path = setup_test_environment / "profiles.json"
    with open(profiles_path) as f:
        profiles = json.load(f)
    
    agent1_id = f"{agent1.name}_lmagent"
    profile = profiles[agent1_id]
    
    assert profile["stats"]["total_games"] == 2
    assert len(profile["game_history"]) == 2

def test_lm_agent_response_processing(setup_test_environment, test_lm_agent):
    """Test that LM responses are properly processed into game moves"""
    agent = test_lm_agent("Test Player", "x >= 3")
    config = create_test_game_config()
    game = InfiniteContractGame(agent, test_lm_agent("Opponent", "y >= 3"), config)
    
    # Initialize available cards
    game.available_cards = game._get_available_cards()
    
    # Test response parsing using game's parser
    response = """
SCRATCH PAD:
Looking at current state and considering options.

SELECTED CARD: 1
"""
    
    # Use game's parse_response method
    scratch_pad, card_number = game._parse_response(response)
    
    # Verify parsed components
    assert scratch_pad.strip() == "Looking at current state and considering options."
    assert card_number == 1

@patch('litellm.completion')
def test_card_type_tracking(mock_completion, setup_test_environment, test_lm_agent):
    mock_completion.return_value = MOCK_RESPONSE
    
    config = create_test_game_config()
    agent1 = test_lm_agent("Test Player 1", "x >= 3")
    agent2 = test_lm_agent("Test Player 2", "y >= 3")
    
    game = InfiniteContractGame(agent1, agent2, config)
    
    # Play until game ends
    while game.play_turn():
        pass
    
    # Verify card type statistics were recorded
    profiles_path = setup_test_environment / "profiles.json"
    with open(profiles_path) as f:
        profiles = json.load(f)
    
    agent1_id = f"{agent1.name}_lmagent"
    profile = profiles[agent1_id]
    
    # Check that card type stats exist and have non-zero values
    stats = profile["stats"]["card_type_stats"]
    total_cards = sum(stats[cat] for cat in ["aggressive", "defensive", "strategic", "utility"])
    assert total_cards > 0, "No card usage was recorded"
    
    # Check that cards_per_game has entries
    assert len(stats["cards_per_game"]) > 0, "No per-game card statistics recorded"

def test_invalid_response_handling(setup_test_environment, test_lm_agent):
    """Test handling of invalid LLM responses"""
    agent1 = test_lm_agent("Test Player 1", "x >= 3")
    agent2 = test_lm_agent("Test Player 2", "y >= 3")
    config = create_test_game_config()
    game = InfiniteContractGame(agent1, agent2, config)
    
    # Initialize available_cards
    game.available_cards = game._get_available_cards()
    
    # Test missing card number
    with pytest.raises(ValueError, match="Invalid response format"):
        game._parse_response("""
SCRATCH PAD:
Some thinking

SELECTED CARD: [no selection]
""")
    
    # Test out of range card number
    with pytest.raises(ValueError, match="Card number .* out of valid range"):
        game._parse_response("""
SCRATCH PAD:
Some thinking

SELECTED CARD: 999
""")
    
    # Test missing SELECTED CARD section
    with pytest.raises(ValueError, match="No 'SELECTED CARD:' section found"):
        game._parse_response("""
SCRATCH PAD:
Some thinking only
""")

@patch('litellm.completion')
def test_invalid_move_handling(mock_completion, setup_test_environment, test_lm_agent):
    # Create agents first
    agent1 = test_lm_agent("Test Player 1", "x >= 3")
    agent2 = test_lm_agent("Test Player 2", "y >= 3")
    
    # Now patch the agent's get_response method directly
    with patch.object(agent1, 'get_response', return_value="""
SCRATCH PAD:
Invalid move test

INVALID FORMAT - NO SELECTED CARD SECTION
"""):
        config = create_test_game_config()
        game = InfiniteContractGame(agent1, agent2, config)
        game.available_cards = game._get_available_cards()
        
        # Play one turn with invalid move
        game.play_turn()
        
        # Verify turn was recorded as failed
        assert len(game._game_result["turn_history"]) == 1
        turn = game._game_result["turn_history"][0]
        assert turn["success"] == False
        assert "error" in turn
        assert "No 'SELECTED CARD:' section found" in turn["error"]