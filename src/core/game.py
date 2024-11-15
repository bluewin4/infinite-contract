from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

from .contract import CodeContract
from .history import GameHistory
from ..agents.base_agent import BaseAgent
from .cards import CardLibrary, CardType, Card
import random

@dataclass
class GameConfig:
    max_turns: int = 50
    memory_window: int = 5
    card_library: CardLibrary = None
    cards_per_turn: int = 3
    get_allowed_cards: Callable[[str], List[CardType]] = None

class InfiniteContractGame:
    def __init__(self, agent1: BaseAgent, agent2: BaseAgent, config: GameConfig):
        self.contract = CodeContract()
        self.history = GameHistory()
        self.agents = {'agent1': agent1, 'agent2': agent2}
        self.config = config
        self.current_player = 'agent1'
        self.current_code = []  # Track the current turn's code
        self.game_over = False
        self.winner = None
        
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
        """Play a single turn of the game. Returns False if game is over."""
        if self.game_over:
            return False
            
        agent = self.agents[self.current_player]
        
        # Create and send prompt
        prompt = self.create_turn_prompt()
        response = agent.get_response(prompt)
        
        # Extract selected card and thought process
        selected_card = self._extract_selected_card(response)
        
        # Apply the selected card and update contract state
        if selected_card is not None:
            selected_card_obj = self.available_cards[selected_card - 1]
            # Apply the new card to existing contract
            self.contract.apply_card(selected_card_obj)
            # Execute the full contract
            self.contract._execute_contract()
            
        # Record the turn in history
        self.history.add_turn(
            turn_number=len(self.history.turns) + 1,
            player_name=self.current_player,
            thought_process=response,
            selected_card=selected_card,
            contract_state=self.contract.current_code.copy(),
            variables=dict(self.contract.variables)
        )
        
        # Check victory conditions after turn
        for player_id, agent in self.agents.items():
            if self.contract.check_victory_condition(agent.victory_condition):
                self.game_over = True
                self.winner = agent.name
                self._update_agent_profiles()  # New method call
                return False
                
        # Check if max turns reached
        if len(self.history.turns) >= self.config.max_turns:
            self.game_over = True
            self._update_agent_profiles()  # New method call
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
        self.current_player = 'agent2' if self.current_player == 'agent1' else 'agent1'

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
        """Get available cards for the current player using weighted selection"""
        agent = self.agents[self.current_player]
        # Get allowed card types based on the player's target variable
        allowed_types = self.config.get_allowed_cards(agent.target_var)
        
        all_cards = []
        for card_type in allowed_types:
            all_cards.extend(self.config.card_library.get_cards_by_type(card_type))
            
        # Get weights for available cards
        weights = [card.frequency for card in all_cards]
        
        # Use weighted random sampling
        return random.choices(
            all_cards, 
            weights=weights, 
            k=min(len(all_cards), self.config.cards_per_turn)
        )

    def _parse_response(self, response: str) -> tuple[str, int]:
        """Parse agent response into scratch pad and card number"""
        try:
            parts = response.split("SELECTED CARD:")
            scratch_pad = parts[0].replace("SCRATCH PAD:", "").strip()
            card_number = int(parts[1].strip())
            return scratch_pad, card_number
        except Exception as e:
            raise ValueError(f"Invalid response format: {e}")

    def _update_agent_profiles(self):
        """Update profiles for both agents when game ends"""
        game_result = {
            "winner": self.winner or "Draw",
            "total_turns": len(self.history.turns),
            "victory_condition": (
                f"{self.winner} achieved victory condition" 
                if self.winner 
                else "Game ended in draw"
            )
        }
        
        # Update both agents' profiles
        for agent in self.agents.values():
            if hasattr(agent, 'update_profile'):  # Check if agent supports profiles
                agent.update_profile(game_result)