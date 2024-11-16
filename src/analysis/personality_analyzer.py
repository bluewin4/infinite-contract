from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
from pathlib import Path
import numpy as np

@dataclass
class PersonalityMetrics:
    aggression_score: float
    risk_taking: float
    adaptability: float
    consistency: float
    win_rate: float
    favorite_moves: Dict[str, float]

class PersonalityAnalyzer:
    def __init__(self, profiles_path: str = "storage/profiles.json"):
        self.profiles_path = Path(profiles_path)
        
    def analyze_personality(self, agent_id: str) -> Optional[PersonalityMetrics]:
        with open(self.profiles_path) as f:
            profiles = json.load(f)
            
        if agent_id not in profiles:
            return None
            
        profile = profiles[agent_id]
        
        # Get stats either from game_history or stats section
        if "stats" in profile and "card_type_stats" in profile["stats"]:
            # Use pre-calculated stats
            stats = profile["stats"]
            card_stats = stats["card_type_stats"]
            
            total_moves = sum(card_stats.get(move_type, 0) 
                             for move_type in ["aggressive", "defensive", "strategic", "utility"])
            
            if total_moves == 0:
                return None
                
            # Calculate metrics from card stats
            aggression = card_stats.get("aggressive", 0) / max(1, card_stats.get("defensive", 0))
            risk_taking = card_stats.get("strategic", 0) / max(1, total_moves)
            
            # Calculate move diversity from cards_per_game
            move_distributions = []
            for game_cards in card_stats.get("cards_per_game", []):
                total = sum(game_cards.values())
                if total > 0:
                    dist = {k: v/total for k, v in game_cards.items()}
                    move_distributions.append(dist)
                    
            adaptability = self._calculate_move_diversity(move_distributions)
            
            # Calculate game length consistency
            game_lengths = [game["total_turns"] for game in profile.get("game_history", [])]
            consistency = 1.0 - (np.std(game_lengths) / (np.mean(game_lengths) + 1)) if game_lengths else 0.0
            
            # Calculate favorite moves
            favorite_moves = {
                move_type: count / max(1, total_moves)
                for move_type, count in card_stats.items()
                if move_type != "cards_per_game"
            }
            
            return PersonalityMetrics(
                aggression_score=aggression,
                risk_taking=risk_taking,
                adaptability=adaptability,
                consistency=consistency,
                win_rate=stats.get("win_rate", 0.0),
                favorite_moves=favorite_moves
            )
            
        # If no pre-calculated stats, try to calculate from game history
        game_history = profile.get("game_history", [])
        if not game_history:
            return None
            
        # Calculate win rate
        wins = sum(1 for game in game_history if game["winner"] == profile["name"])
        win_rate = wins / len(game_history)
        
        # Analyze move patterns
        move_counts = {"aggressive": 0, "defensive": 0, "strategic": 0, "utility": 0}
        for game in game_history:
            if "card_usage" in game:
                for move_type, count in game["card_usage"].items():
                    move_counts[move_type] += count
                    
        total_moves = sum(move_counts.values())
        if total_moves == 0:
            return None
            
        # Calculate metrics
        aggression = move_counts["aggressive"]
        risk_taking = move_counts["strategic"]
        
        # Calculate move diversity per game
        move_distributions = []
        for game in game_history:
            if "card_usage" in game:
                total = sum(game["card_usage"].values())
                if total > 0:
                    dist = {k: v/total for k, v in game["card_usage"].items()}
                    move_distributions.append(dist)
                    
        adaptability = self._calculate_move_diversity(move_distributions)
        
        # Calculate game length consistency
        game_lengths = [game["total_turns"] for game in game_history]
        consistency = 1.0 - (np.std(game_lengths) / (np.mean(game_lengths) + 1))
        
        # Calculate favorite moves
        favorite_moves = move_counts.copy()
        
        return PersonalityMetrics(
            aggression_score=aggression,
            risk_taking=risk_taking,
            adaptability=adaptability,
            consistency=consistency,
            win_rate=win_rate,
            favorite_moves=favorite_moves
        )
    
    def _calculate_move_diversity(self, distributions: List[Dict[str, float]]) -> float:
        if not distributions:
            return 0.0
            
        # Calculate average distribution
        avg_dist = {}
        for dist in distributions:
            for move_type, freq in dist.items():
                avg_dist[move_type] = avg_dist.get(move_type, 0) + freq / len(distributions)
                
        # Calculate variance from average
        variances = []
        for dist in distributions:
            variance = sum((dist.get(k, 0) - avg_dist.get(k, 0))**2 for k in avg_dist)
            variances.append(variance)
            
        return 1.0 - np.mean(variances)
    
    def compare_personalities(self, agent1_id: str, agent2_id: str) -> Dict[str, Any]:
        """Compare personality metrics between two agents"""
        # Get metrics for both agents
        metrics1 = self.analyze_personality(agent1_id)
        metrics2 = self.analyze_personality(agent2_id)
        
        # Return empty dict if either agent doesn't exist
        if not metrics1 or not metrics2:
            return {}
            
        # Calculate differences in key metrics
        return {
            "aggression_difference": metrics1.aggression_score - metrics2.aggression_score,
            "risk_taking_difference": metrics1.risk_taking - metrics2.risk_taking,
            "adaptability_difference": metrics1.adaptability - metrics2.adaptability,
            "consistency_difference": metrics1.consistency - metrics2.consistency,
            "win_rate_difference": metrics1.win_rate - metrics2.win_rate,
            "move_preference_similarity": self._calculate_move_similarity(
                metrics1.favorite_moves,
                metrics2.favorite_moves
            )
        }
    
    def _calculate_move_similarity(self, moves1: Dict[str, float], moves2: Dict[str, float]) -> float:
        """Calculate similarity between two agents' move preferences"""
        all_moves = set(moves1.keys()) | set(moves2.keys())
        similarity = 0.0
        
        for move in all_moves:
            val1 = moves1.get(move, 0.0)
            val2 = moves2.get(move, 0.0)
            similarity += 1.0 - abs(val1 - val2)
            
        return similarity / max(1, len(all_moves))