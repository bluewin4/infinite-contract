import argparse
from pathlib import Path
import matplotlib.pyplot as plt
from src.analysis.personality_visualizer import PersonalityVisualizer
import json
import seaborn as sns
import pandas as pd

def setup_plotting_style():
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = [12, 8]

def create_output_directory(base_path: str) -> Path:
    output_dir = Path(base_path) / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def analyze_all_profiles(profiles_path: str, output_dir: Path):
    visualizer = PersonalityVisualizer(profiles_path)
    
    with open(profiles_path) as f:
        profiles = json.load(f)
    
    # Group agents by personality type
    personality_groups = {}
    for agent_id, profile in profiles.items():
        personality = profile.get("personality", "No personality")
        if personality not in personality_groups:
            personality_groups[personality] = []
        personality_groups[personality].append(agent_id)

    # Create comparison visualizations
    for personality, agents in personality_groups.items():
        if len(agents) > 0:
            # Individual agent analysis
            for agent_id in agents:
                # Personality metrics radar chart
                fig = visualizer.plot_personality_metrics(agent_id)
                if fig:
                    fig.savefig(output_dir / f"{agent_id}_metrics.png")
                    plt.close(fig)
                
                # Move distribution pie chart
                fig = visualizer.plot_move_distribution(agent_id)
                if fig:
                    fig.savefig(output_dir / f"{agent_id}_moves.png")
                    plt.close(fig)
                
                # Strategy evolution line plot
                fig = visualizer.plot_strategy_evolution(agent_id)
                if fig:
                    fig.savefig(output_dir / f"{agent_id}_strategy.png")
                    plt.close(fig)

    # Create personality group comparisons
    fig = visualizer.plot_win_rate_comparison(list(profiles.keys()))
    if fig:
        fig.savefig(output_dir / "win_rate_comparison.png")
        plt.close(fig)

def main():
    parser = argparse.ArgumentParser(description='Generate visualizations for personality profiles')
    parser.add_argument('--profiles', default='storage/profiles.json', 
                       help='Path to profiles.json file')
    parser.add_argument('--output', default='analysis_output',
                       help='Output directory for visualizations')
    
    args = parser.parse_args()
    
    setup_plotting_style()
    output_dir = create_output_directory(args.output)
    
    print(f"Analyzing profiles from: {args.profiles}")
    print(f"Saving visualizations to: {output_dir}")
    
    analyze_all_profiles(args.profiles, output_dir)
    print("Analysis complete!")

if __name__ == "__main__":
    main() 