import pytest
from datetime import datetime, timedelta
from src.core.analytics import GameAnalytics, GameResult, PlayerProfile
from src.core.history import GameHistory, TurnRecord
from src.core.cards import CardType
from src.core.game import InfiniteContractGame, GameConfig
from src.agents.base_agent import SimpleAgent
from src.core.cards import CardLibrary
import os
import json
import shutil

@pytest.fixture
def sample_turn_record():
    return TurnRecord(
        turn_number=1,
        player_name="Player 1",
        thought_process="Testing move",
        selected_card=1,
        contract_state=["x = 0", "y = 0"],
        variables={"x": 0, "y": 0}
    )

@pytest.fixture
def test_analytics():
    # Use a test-specific directory
    analytics = GameAnalytics(storage_path="test_game_data")
    yield analytics
    # Cleanup after tests
    if os.path.exists("test_game_data"):
        shutil.rmtree("test_game_data")

def test_game_history_storage():
    history = GameHistory()
    
    # Add multiple turns
    for i in range(3):
        history.add_turn(
            turn_number=i + 1,
            player_name=f"Player {i % 2 + 1}",
            thought_process=f"Turn {i} thinking",
            selected_card=i,
            contract_state=[f"x = {i}"],
            variables={"x": i}
        )
    
    # Test retrieval
    assert len(history.turns) == 3
    assert history.get_turn(1).turn_number == 1
    assert len(history.get_recent_turns(2)) == 2
    assert len(history.get_player_turns("Player 1")) == 2

def test_analytics_profile_creation(test_analytics):
    # Record a game
    game_history = [
        TurnRecord(
            turn_number=1,
            player_name="Player 1",
            thought_process="Test move",
            selected_card=1,
            contract_state=["x = 0"],
            variables={"x": 0}
        )
    ]
    
    test_analytics.record_game(
        game_history=game_history,
        winner="Player 1",
        players={"Player 1": "test-model", "Player 2": "test-model"},
        victory_conditions={"Player 1": "x >= 5", "Player 2": "x >= 5"},
        model_params={
            "Player 1": {"temperature": 0.7, "max_tokens": 500},
            "Player 2": {"temperature": 0.7, "max_tokens": 500}
        }
    )
    
    # Check profile creation
    profile = test_analytics.player_profiles.get("Player 1_test-model")
    assert profile is not None
    assert profile.stats.total_games == 1
    assert profile.stats.games_won == 1

def test_analytics_persistence(test_analytics):
    # Record initial game
    game_history = [
        TurnRecord(
            turn_number=1,
            player_name="Player 1",
            thought_process="Test move",
            selected_card=1,
            contract_state=["x = 0"],
            variables={"x": 0}
        )
    ]
    
    test_analytics.record_game(
        game_history=game_history,
        winner="Player 1",
        players={"Player 1": "test-model", "Player 2": "test-model"},
        victory_conditions={"Player 1": "x >= 5", "Player 2": "x >= 5"},
        model_params={
            "Player 1": {"temperature": 0.7, "max_tokens": 500},
            "Player 2": {"temperature": 0.7, "max_tokens": 500}
        }
    )
    
    # Create new analytics instance to test loading
    new_analytics = GameAnalytics(storage_path="test_game_data")
    
    # Verify data persisted
    profile = new_analytics.player_profiles.get("Player 1_test-model")
    assert profile is not None
    assert profile.stats.total_games == 1
    assert len(profile.game_history) == 1

def test_player_analysis(test_analytics):
    # Record multiple games with different outcomes
    for i in range(5):
        game_history = [
            TurnRecord(
                turn_number=1,
                player_name="Player 1",
                thought_process=f"Game {i} move",
                selected_card=1,  # Using card ID 1 which we know is AGGRESSIVE
                contract_state=["x = 0"],
                variables={"x": 0}
            )
        ]
        
        test_analytics.record_game(
            game_history=game_history,
            winner="Player 1" if i % 2 == 0 else "Player 2",
            players={"Player 1": "test-model", "Player 2": "test-model"},
            victory_conditions={"Player 1": "x >= 5", "Player 2": "x >= 5"},
            model_params={
                "Player 1": {"temperature": 0.7, "max_tokens": 500},
                "Player 2": {"temperature": 0.7, "max_tokens": 500}
            }
        )
    
    # Get analysis
    analysis = test_analytics.get_player_analysis("Player 1", "test-model")
    
    assert analysis is not None
    assert analysis["win_rate"] == pytest.approx(0.6)  # Won 3 out of 5 games
    assert "recent_performance" in analysis
    assert "favorite_strategies" in analysis
    assert analysis["favorite_strategies"]["AGGRESSIVE"] == 1.0  # All moves were aggressive

def test_game_data_storage():
    # Create a test game
    config = GameConfig(
        max_turns=5,
        memory_window=3,
        card_library=CardLibrary(),
        allowed_card_types=[CardType.AGGRESSIVE],
        cards_per_turn=1
    )
    
    agent1 = SimpleAgent("Player 1", "x >= 5")
    agent2 = SimpleAgent("Player 2", "x <= -5")
    
    # Create game with test-specific storage
    game = InfiniteContractGame(agent1, agent2, config)
    game.analytics = GameAnalytics(storage_path="test_storage")
    
    # Run game until completion
    while game.play_turn():
        pass
        
    # Verify data was stored
    assert os.path.exists("test_storage/profiles.json")
    
    # Load and verify contents
    with open("test_storage/profiles.json", 'r') as f:
        stored_data = json.load(f)
        
    # Check if both players are in the stored data
    assert "Player 1_simple" in stored_data
    assert "Player 2_simple" in stored_data
    
    # Verify profile structure for Player 1
    player1_data = stored_data["Player 1_simple"]
    assert player1_data["name"] == "Player 1"
    assert player1_data["model_type"] == "simple"
    assert "stats" in player1_data
    assert "total_games" in player1_data["stats"]
    assert "games_won" in player1_data["stats"]
    assert "game_history" in player1_data
    
    # Cleanup
    shutil.rmtree("test_storage")