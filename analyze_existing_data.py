from src.analysis.analyze_games import StrategyAnalyzer
from src.analysis.visualize import plot_strategy_evolution, plot_comparative_analysis
from src.core.analytics import GameAnalytics

def analyze_existing_data():
    # Initialize analytics with the path where your data is stored
    analytics = GameAnalytics("game_data")  # This will load existing profiles
    
    # Create analyzer
    analyzer = StrategyAnalyzer(analytics)
    
    # Plot individual analysis for each player
    plot_strategy_evolution(analyzer, "Player 1", "claude-3-haiku-20240307")
    plot_strategy_evolution(analyzer, "Player 2", "claude-3-haiku-20240307")
    
    # Plot comparative analysis
    players = [
        {"name": "Player 1", "model": "claude-3-haiku-20240307"},
        {"name": "Player 2", "model": "claude-3-haiku-20240307"}
    ]
    plot_comparative_analysis(analyzer, players)

if __name__ == "__main__":
    analyze_existing_data() 