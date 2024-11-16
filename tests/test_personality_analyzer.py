import pytest
from src.analysis.personality_analyzer import PersonalityAnalyzer, PersonalityMetrics
from pathlib import Path
import json

@pytest.fixture
def test_profiles(tmp_path):
    profiles = {
        "Player 1_chaotic_test-model_0.7": {
            "name": "Player 1",
            "personality": "Chaotic and aggressive",
            "stats": {
                "total_games": 10,
                "games_won": 7,
                "win_rate": 0.7,
                "avg_turns_to_win": 5,
                "card_type_stats": {
                    "aggressive": 15,
                    "defensive": 5,
                    "strategic": 8,
                    "utility": 2,
                    "cards_per_game": [
                        {"aggressive": 2, "defensive": 1, "strategic": 1, "utility": 0},
                        {"aggressive": 1, "defensive": 0, "strategic": 2, "utility": 1}
                    ]
                }
            },
            "game_history": [
                {"total_turns": 5, "winner": "Player 1"},
                {"total_turns": 6, "winner": "Player 1"}
            ]
        }
    }
    
    profiles_path = tmp_path / "test_profiles.json"
    with open(profiles_path, 'w') as f:
        json.dump(profiles, f)
    
    return profiles_path

def test_personality_analysis(test_profiles):
    analyzer = PersonalityAnalyzer(str(test_profiles))
    metrics = analyzer.analyze_personality("Player 1_chaotic_test-model_0.7")
    
    assert metrics is not None
    assert metrics.win_rate == 0.7
    assert metrics.consistency > 0
    
    # Test move type distribution
    assert "aggressive" in metrics.favorite_moves
    assert metrics.favorite_moves["aggressive"] > metrics.favorite_moves["defensive"]
    
    # Test that metrics are calculated
    assert metrics.aggression_score >= 0
    assert 0 <= metrics.risk_taking <= 1
    assert 0 <= metrics.adaptability <= 1

def test_personality_comparison(test_profiles):
    analyzer = PersonalityAnalyzer(str(test_profiles))
    
    # Should return empty dict for invalid comparison
    result = analyzer.compare_personalities(
        "Player 1_chaotic_test-model_0.7",
        "NonexistentPlayer"
    )
    assert result == {} 