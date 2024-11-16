from typing import Dict, List
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
import json
from .personality_analyzer import PersonalityAnalyzer
import numpy as np

class PersonalityVisualizer:
    def __init__(self, profiles_path: str = "storage/profiles.json"):
        self.profiles_path = Path(profiles_path)
        self.analyzer = PersonalityAnalyzer(str(profiles_path))
        
    def load_profiles(self) -> Dict:
        with open(self.profiles_path) as f:
            return json.load(f)
            
    def plot_personality_metrics(self, agent_id: str):
        """Create a radar chart of personality metrics"""
        metrics = self.analyzer.analyze_personality(agent_id)
        if not metrics:
            return
            
        # Prepare data for radar chart
        categories = ['Aggression', 'Risk Taking', 'Adaptability', 'Consistency']
        values = [
            metrics.aggression_score,
            metrics.risk_taking,
            metrics.adaptability,
            metrics.consistency
        ]
        
        # Create radar chart
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
        values = np.concatenate((values, [values[0]]))  # complete the circle
        angles = np.concatenate((angles, [angles[0]]))  # complete the circle
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_title(f"Personality Profile: {agent_id}")
        
        return fig

    def plot_move_distribution(self, agent_id: str):
        """Create a pie chart of move type distribution"""
        metrics = self.analyzer.analyze_personality(agent_id)
        if not metrics:
            return
            
        # Create pie chart of move preferences
        fig, ax = plt.subplots(figsize=(8, 8))
        moves = metrics.favorite_moves
        plt.pie(moves.values(), labels=moves.keys(), autopct='%1.1f%%')
        plt.title(f"Move Distribution: {agent_id}")
        
        return fig

    def plot_win_rate_comparison(self, agent_ids: List[str]):
        """Create a bar chart comparing win rates"""
        win_rates = []
        labels = []
        
        for agent_id in agent_ids:
            metrics = self.analyzer.analyze_personality(agent_id)
            if metrics:
                win_rates.append(metrics.win_rate)
                labels.append(agent_id.split('_')[0])  # Just use player name
                
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=labels, y=win_rates)
        plt.title("Win Rate Comparison")
        plt.ylabel("Win Rate")
        
        return fig

    def plot_strategy_evolution(self, agent_id: str):
        """Plot how move preferences change over time"""
        profiles = self.load_profiles()
        if agent_id not in profiles:
            return
            
        profile = profiles[agent_id]
        games = profile.get("game_history", [])
        
        # Prepare data for line plot
        move_types = ["aggressive", "defensive", "strategic", "utility"]
        game_numbers = []
        move_counts = {move_type: [] for move_type in move_types}
        
        for i, game in enumerate(games):
            game_numbers.append(i + 1)
            card_usage = game.get("card_usage", {})
            for move_type in move_types:
                move_counts[move_type].append(card_usage.get(move_type, 0))
                
        # Create line plot
        fig, ax = plt.subplots(figsize=(12, 6))
        for move_type in move_types:
            plt.plot(game_numbers, move_counts[move_type], label=move_type, marker='o')
            
        plt.title(f"Strategy Evolution: {agent_id}")
        plt.xlabel("Game Number")
        plt.ylabel("Number of Moves")
        plt.legend()
        
        return fig 