from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .contract import CodeContract
from .history import GameHistory
from ..agents.base_agent import BaseAgent
from .cards import CardLibrary, CardType, Card
from .analytics import GameAnalytics

@dataclass
class GameConfig:
    max_turns: int = 5
    memory_window: int = 5
    card_library: CardLibrary = None
    allowed_card_types: List[CardType] = None
    cards_per_turn: int = 3

class InfiniteContractGame:
    def __init__(self, agent1: BaseAgent, agent2: BaseAgent, config: GameConfig):
        self.contract = CodeContract()
        self.history = GameHistory()
        self.agents = {agent1.name: agent1, agent2.name: agent2}
        self.config = config
        self.analytics = GameAnalytics()
        self.current_player = agent1.name
        self.turn_count = 0
        
        # Initialize game history with agent information
        self.history.initialize_game(self.agents)
        
    def create_turn_prompt(self) -> str:
        """Create the prompt for current turn"""
        agent = self.agents[self.current_player]
        recent_history = self.history.get_recent_turns(self.config.memory_window)
        
        # Get available cards for this turn
        self.available_cards = self._get_available_cards()
        
        return f"""
=== Infinite Contract Game - Turn {len(self.history.turns) + 1} ===

Current Contract Contents:
{self._format_contract()}

Variable States:
{self._format_variables()}

Game History (Last {self.config.memory_window} Turns):
{self._format_history(recent_history)}

Your Victory Condition: {agent.victory_condition}

Available Cards:
{self._format_cards()}

Your Strategy Notes:
{self._format_notes(agent.strategy_notes)}

Think through your move, considering:
1. Current contract state
2. Execution order of code
3. Previous moves and their effects
4. Path to victory condition

Format your response as:
SCRATCH PAD:
[your strategic thinking]

SELECTED CARD: [number]
"""

    def play_turn(self) -> bool:
        """Execute a single turn"""
        # Increment turn count first
        self.turn_count += 1
        
        # Check turn limit
        if self.turn_count > self.config.max_turns:
            print(f"\nGame ended: Maximum turns ({self.config.max_turns}) reached")
            self.end_game(None)  # Changed from _handle_victory to end_game
            return False
            
        agent = self.agents[self.current_player]
        
        # Create and send prompt
        prompt = self.create_turn_prompt()
        response = agent.get_response(prompt)
        
        # Extract selected card and thought process
        selected_card = self._extract_selected_card(response)
        
        # Apply the selected card
        if selected_card is not None:
            self.contract.apply_card(self.available_cards[selected_card - 1])
            
        # Record the turn in history
        self.history.add_turn(
            turn_number=self.turn_count,
            player_name=self.current_player,
            thought_process=response,
            selected_card=selected_card,
            contract_state=self.contract.current_code,
            variables=self.contract.variables
        )
        
        # Check victory conditions
        for player_name, agent in self.agents.items():
            if self.contract.check_victory_condition(agent.victory_condition):
                print(f"\n{player_name} has won!")
                self._handle_victory(player_name)
                return False
        
        # Switch players
        self._switch_players()
        return True

    def _extract_selected_card(self, response: str) -> Optional[int]:
        """Extract the selected card number from the response"""
        try:
            parts = response.split("SELECTED CARD:")
            if len(parts) > 1:
                card_number = int(parts[1].strip())
                if 1 <= card_number <= len(self.available_cards):
                    return card_number
            return None
        except ValueError:
            return None

    def _switch_players(self):
        """Switch to the next player"""
        player_names = list(self.agents.keys())
        self.current_player = player_names[1] if self.current_player == player_names[0] else player_names[0]

    def _format_contract(self) -> str:
        return "\n".join(f"{i}: {line}" for i, line in enumerate(self.contract.current_code))

    def _format_variables(self) -> str:
        return "\n".join(f"{k}: {v}" for k, v in self.contract.variables.items())

    def _format_history(self, history) -> str:
        return "\n".join(
            f"Turn {turn.turn_number}: Player {turn.player_name} played card {turn.selected_card} - Variables: {turn.variables}"
            for turn in history
        )

    def _format_cards(self) -> str:
        available_cards = self._get_available_cards()
        return "\n".join(f"{i+1}. {card.name}: {card.description}" 
                        for i, card in enumerate(available_cards))

    def _format_notes(self, notes: List[str]) -> str:
        return "\n".join(notes[-self.config.memory_window:])

    def _get_available_cards(self) -> List[Card]:
        all_cards = []
        for card_type in self.config.allowed_card_types:
            all_cards.extend(self.config.card_library.get_cards_by_type(card_type))
        # Randomly select cards_per_turn number of cards
        import random
        return random.sample(all_cards, min(len(all_cards), self.config.cards_per_turn))

    def _parse_response(self, response: str) -> tuple[str, int]:
        """Parse agent response into scratch pad and card number"""
        try:
            parts = response.split("SELECTED CARD:")
            scratch_pad = parts[0].replace("SCRATCH PAD:", "").strip()
            card_number = int(parts[1].strip())
            return scratch_pad, card_number
        except Exception as e:
            raise ValueError(f"Invalid response format: {e}")

    def _handle_victory(self, winner: str):
        """Handle game victory and record analytics"""
        # Update game history with final state
        self.history.finalize_game(winner)
        
        # Record in analytics
        players = {
            agent.name: getattr(agent, 'model', 'simple')  # Use agent.name instead of dict key
            for name, agent in self.agents.items()
        }
        victory_conditions = {
            agent.name: agent.victory_condition 
            for name, agent in self.agents.items()
        }
        
        self.analytics.record_game(
            game_history=self.history.turns,
            winner=winner,
            players=players,
            victory_conditions=victory_conditions
        )

    def end_game(self, winner: Optional[str] = None):
        """End the game and save history"""
        self.history.finalize_game(winner)
        if hasattr(self, 'analytics'):
            # Get the actual agent names
            players = {
                agent.name: getattr(agent, 'model', 'simple')  # Use agent.name instead of dict key
                for name, agent in self.agents.items()
            }
            victory_conditions = {
                agent.name: agent.victory_condition 
                for name, agent in self.agents.items()
            }
            
            self.analytics.record_game(
                game_history=self.history.turns,
                winner=winner,
                players=players,
                victory_conditions=victory_conditions
            )