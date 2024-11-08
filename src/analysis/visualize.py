import matplotlib.pyplot as plt
from typing import List, Dict
from datetime import datetime, timedelta

def plot_strategy_evolution(analyzer, player_name: str, model_type: str):
    """Plot the evolution of player's strategy over time"""
    analysis = analyzer.analyze_player(player_name, model_type)
    
    # Create figure with multiple subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Win Rate Trend
    win_rates = analysis["performance_trend"]["win_rate_history"]
    if win_rates:
        ax1.plot(win_rates, 'b-', label="Win Rate (5-game moving average)")
        ax1.set_title(f"Win Rate Trend - {player_name}")
        ax1.set_xlabel("Games")
        ax1.set_ylabel("Win Rate")
        ax1.grid(True)
        ax1.legend()
    
    # Plot 2: Strategy Distribution
    strategy_data = analysis["card_preferences"]
    if strategy_data:
        strategies = list(strategy_data.keys())
        usage = list(strategy_data.values())
        ax2.bar(strategies, usage)
        ax2.set_title("Strategy Distribution")
        ax2.set_xlabel("Card Types")
        ax2.set_ylabel("Usage Frequency")
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # Save plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"strategy_analysis_{player_name}_{timestamp}.png"
    plt.savefig(filename)
    plt.close()
    
    print(f"Strategy evolution plot saved as {filename}")

def plot_comparative_analysis(analyzer, players: List[Dict[str, str]]):
    """Plot comparative analysis of multiple players"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Collect data for all players
    win_rates = []
    aggressive_ratios = []
    defensive_ratios = []
    adaptability_scores = []
    names = []
    
    for player in players:
        analysis = analyzer.analyze_player(player["name"], player["model"])
        names.append(player["name"])
        win_rates.append(analysis["overall_stats"]["win_rate"])
        
        patterns = analysis["strategy_patterns"]
        aggressive_ratios.append(patterns["aggressive_ratio"])
        defensive_ratios.append(patterns["defensive_ratio"])
        adaptability_scores.append(analysis["adaptability"]["adaptability_score"])
    
    # Plot 1: Win Rates
    axes[0, 0].bar(names, win_rates)
    axes[0, 0].set_title("Win Rates")
    axes[0, 0].set_ylabel("Win Rate")
    
    # Plot 2: Strategy Balance
    width = 0.35
    x = range(len(names))
    axes[0, 1].bar([i - width/2 for i in x], aggressive_ratios, width, label='Aggressive')
    axes[0, 1].bar([i + width/2 for i in x], defensive_ratios, width, label='Defensive')
    axes[0, 1].set_title("Strategy Balance")
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(names)
    axes[0, 1].legend()
    
    # Plot 3: Adaptability Scores
    axes[1, 0].bar(names, adaptability_scores)
    axes[1, 0].set_title("Adaptability Scores")
    axes[1, 0].set_ylabel("Score")
    
    # Plot 4: Performance Over Time
    for player in players:
        analysis = analyzer.analyze_player(player["name"], player["model"])
        win_history = analysis["performance_trend"]["win_rate_history"]
        if win_history:
            axes[1, 1].plot(win_history, label=player["name"])
    
    axes[1, 1].set_title("Performance Trend")
    axes[1, 1].set_xlabel("Games")
    axes[1, 1].set_ylabel("Win Rate")
    axes[1, 1].legend()
    
    plt.tight_layout()
    
    # Save plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comparative_analysis_{timestamp}.png"
    plt.savefig(filename)
    plt.close()
    
    print(f"Comparative analysis plot saved as {filename}")