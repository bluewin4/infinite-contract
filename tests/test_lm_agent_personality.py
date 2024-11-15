import pytest
from unittest.mock import patch
from src.agents.lm_agent import LMAgent
from src.core.game import InfiniteContractGame
from tests.test_lm_agent import (
    create_test_game_config, 
    MOCK_RESPONSE, 
    setup_test_environment
)
import hashlib
import json

@pytest.fixture
def test_personality_agent():
    def _create_agent(name: str, victory_condition: str, personality: str = None):
        return LMAgent(
            name=name,
            model="claude-3-haiku-20240307",
            victory_condition=victory_condition,
            personality=personality,
            temperature=0.7,
            max_tokens=500,
            testing=True
        )
    return _create_agent

@patch('litellm.completion')
def test_personality_profile_creation(mock_completion, setup_test_environment, test_personality_agent):
    mock_completion.return_value = MOCK_RESPONSE
    
    # Create agents with different personalities
    agent1 = test_personality_agent(
        "Test Player", 
        "x >= 3",
        "Aggressive and bold player"
    )
    agent2 = test_personality_agent(
        "Test Player",  # Same name
        "x >= 3",      # Same victory condition
        "Cautious and defensive player"  # Different personality
    )
    
    # Verify different profiles were created
    profiles_path = setup_test_environment / "profiles.json"
    with open(profiles_path) as f:
        profiles = json.load(f)
    
    # Get agent IDs using the same hash method as in LMAgent
    agent1_hash = hashlib.md5(str(agent1.personality).encode()).hexdigest()[:8]
    agent2_hash = hashlib.md5(str(agent2.personality).encode()).hexdigest()[:8]
    
    agent1_id = f"{agent1.name}_{agent1_hash}_{agent1.model}_{agent1.temperature}"
    agent2_id = f"{agent2.name}_{agent2_hash}_{agent2.model}_{agent2.temperature}"
    
    assert agent1_id in profiles
    assert agent2_id in profiles
    assert agent1_id != agent2_id

@patch('litellm.completion')
def test_personality_profile_updates(mock_completion, setup_test_environment, test_personality_agent):
    mock_completion.return_value = MOCK_RESPONSE
    
    config = create_test_game_config()
    agent1 = test_personality_agent(
        "Test Player",
        "x >= 3",
        "Aggressive player"
    )
    agent2 = test_personality_agent(
        "Test Player 2",
        "y >= 3"
    )
    
    # Create and run game
    game = InfiniteContractGame(agent1, agent2, config)
    
    # Play a few turns
    for _ in range(3):
        if not game.play_turn():
            break
    
    # Verify profile updates
    profiles_path = setup_test_environment / "profiles.json"
    with open(profiles_path) as f:
        profiles = json.load(f)
    
    # Get agent ID using hash
    personality_hash = hashlib.md5(str(agent1.personality).encode()).hexdigest()[:8]
    agent_id = f"{agent1.name}_{personality_hash}_{agent1.model}_{agent1.temperature}"
    
    assert agent_id in profiles
    profile = profiles[agent_id]
    
    # Check personality-specific fields
    assert profile["personality"] == agent1.personality
    assert "personality_traits" in profile["stats"]

def test_personality_in_system_prompt(test_personality_agent):
    personality = "I am a risk-taking player who loves chaos!"
    agent = test_personality_agent("Test Player", "x >= 3", personality)
    
    system_prompt = agent._create_system_prompt()
    
    assert personality in system_prompt
    assert "Make your decisions and express your thoughts in alignment with this personality" in system_prompt 