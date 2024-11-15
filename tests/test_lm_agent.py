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
Choosing card 1 to increment x

SELECTED CARD: 1
"""
            })
        })
    ]
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
            max_tokens=500
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
    
    # Test basic response parsing
    response = agent.get_response("""
    Current Contract Contents:
    x = 1
    y = 1
    
    Available Cards:
    1. x += 1
    2. y -= 1
    3. if x > y: x += 1
    """)
    
    # Verify response format
    assert "SCRATCH PAD:" in response
    assert "SELECTED CARD:" in response
    
    # Extract card selection
    card_line = [line for line in response.split('\n') if "SELECTED CARD:" in line][0]
    selected_card = int(card_line.split(':')[1].strip())
    
    # Verify valid card selection
    assert 1 <= selected_card <= 3 