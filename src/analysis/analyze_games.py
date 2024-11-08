from typing import Dict, List
from collections import defaultdict
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from ..core.analytics import GameAnalytics
from ..core.cards import CardType

class StrategyAnalyzer:
    def __init__(self, analytics: GameAnalytics):
        self.analytics = analytics

    def analyze_player(self, player_name: str, model_type: str) -> Dict:
        """Comprehensive analysis of a player's strategy"""
        analysis = self.analytics.get_player_analysis(player_name, model_type)
        if not analysis:
            return {"error": "Player not found"}

        profile = self.analytics.player_profiles.get(f"{player_name}_{model_type}")
        
        return {
            "overall_stats": {
                "win_rate": analysis["win_rate"],
                "avg_turns_to_win": analysis["avg_turns_to_win"],
                "total_games": profile.stats.total_games
            },
            "strategy_patterns": self._analyze_strategy_patterns(profile),
            "card_preferences": analysis["favorite_strategies"],
            "performance_trend": self._analyze_performance_trend(profile),
            "adaptability": self._analyze_adaptability(profile)
        }
    
    def _analyze_strategy_patterns(self, profile) -> Dict:
        """Analyze patterns in player's strategy"""
        patterns = defaultdict(int)
        
        # Look at sequences of moves
        for game in profile.game_history:
            game_moves = [turn.selected_card for turn in game.turns 
                         if turn.player_name == profile.name]
            
            # Analyze card type sequences
            for i in range(len(game_moves) - 2):
                sequence = tuple(game_moves[i:i+3])
                patterns[sequence] += 1
        
        return {
            "common_sequences": dict(sorted(patterns.items(), 
                                         key=lambda x: x[1], 
                                         reverse=True)[:5]),
            "aggressive_ratio": self._calculate_card_type_ratio(profile, CardType.AGGRESSIVE),
            "defensive_ratio": self._calculate_card_type_ratio(profile, CardType.DEFENSIVE)
        }
    
    def _calculate_card_type_ratio(self, profile, card_type: CardType) -> float:
        """Calculate ratio of specific card type usage"""
        total_cards = sum(profile.stats.favorite_card_types.values())
        type_usage = profile.stats.favorite_card_types.get(card_type, 0)
        return type_usage / total_cards if total_cards > 0 else 0
    
    def _analyze_performance_trend(self, profile) -> Dict:
        """Analyze player's performance trend over time"""
        window_size = 5
        wins = []
        current_window = []
        
        for game in profile.game_history:
            current_window.append(1 if game.winner == profile.name else 0)
            if len(current_window) >= window_size:
                wins.append(sum(current_window) / window_size)
                current_window.pop(0)
        
        return {
            "recent_trend": "improving" if len(wins) >= 2 and wins[-1] > wins[0] 
                          else "declining" if len(wins) >= 2 and wins[-1] < wins[0]
                          else "stable",
            "win_rate_history": wins
        }
    
    def _analyze_adaptability(self, profile) -> Dict:
        """Analyze how well player adapts to different situations"""
        strategy_changes = 0
        prev_strategy = None
        
        for game in profile.game_history:
            current_strategy = self._determine_dominant_strategy(game)
            if prev_strategy and current_strategy != prev_strategy:
                strategy_changes += 1
            prev_strategy = current_strategy
        
        return {
            "strategy_changes": strategy_changes,
            "adaptability_score": strategy_changes / len(profile.game_history) 
                                if profile.game_history else 0
        }
    
    def _determine_dominant_strategy(self, game) -> CardType:
        """Determine the dominant strategy used in a game"""
        card_types = defaultdict(int)
        for turn in game.turns:
            card_type = self._get_card_type_from_id(turn.selected_card)
            if card_type:
                card_types[card_type] += 1
        
        return max(card_types.items(), key=lambda x: x[1])[0] if card_types else None
    
    def _get_card_type_from_id(self, card_id: int) -> CardType:
        """Get card type from card ID - implement based on your card system"""
        # This needs to be implemented based on your card system
        # For now returning None to avoid errors
        return None

def plot_strategy_evolution(analyzer: StrategyAnalyzer, player_name: str, model_type: str):
    """Plot the evolution of player's strategy over time"""
    analysis = analyzer.analyze_player(player_name, model_type)
    
    plt.figure(figsize=(12, 6))
    
    # Plot win rate trend
    win_rates = analysis["performance_trend"]["win_rate_history"]
    plt.plot(win_rates, label="Win Rate (5-game moving average)")
    
    # Plot strategy adaptation points
    adaptability = analysis["adaptability"]["strategy_changes"]
    plt.axvline(x=adaptability, color='r', linestyle='--', 
                label="Strategy Change Points")
    
    plt.title(f"Strategy Evolution for {player_name}")
    plt.xlabel("Games")
    plt.ylabel("Win Rate")
    plt.legend()
    plt.grid(True)
    plt.show() 