import pytest
from src.analysis.personality_visualizer import PersonalityVisualizer
import matplotlib.pyplot as plt

@pytest.fixture
def visualizer(test_profiles):
    return PersonalityVisualizer(str(test_profiles))

def test_personality_metrics_plot(visualizer):
    fig = visualizer.plot_personality_metrics("Player 1_chaotic_test-model_0.7")
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_move_distribution_plot(visualizer):
    fig = visualizer.plot_move_distribution("Player 1_chaotic_test-model_0.7")
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_win_rate_comparison(visualizer):
    fig = visualizer.plot_win_rate_comparison(["Player 1_chaotic_test-model_0.7"])
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_strategy_evolution_plot(visualizer):
    fig = visualizer.plot_strategy_evolution("Player 1_chaotic_test-model_0.7")
    assert isinstance(fig, plt.Figure)
    plt.close(fig) 