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
        self._game_result = {
            "turn_history": [],
            "total_turns": 0,
            "winner": None,
            "victory_condition": None
        }
        # Add turn tracking for card usage
        self._current_turn_data = {
            'agent1': [],
            'agent2': []
        }
        
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
        if self.game_over:
            return False
        
        agent = self.agents[self.current_player]
        turn_data = None
        
        try:
            # Get available cards before creating prompt
            self.available_cards = self._get_available_cards()
            
            # Create and send prompt
            prompt = self.create_turn_prompt()
            response = agent.get_response(prompt)
            
            # Extract selected card and thought process
            scratch_pad, card_index = self._parse_response(response)
            
            # Get the selected card object
            selected_card = self.available_cards[card_index - 1]
            
            # Apply the card's effect
            self.contract.add_line(selected_card.code)
            
            # Only record turn data after all operations succeed
            turn_data = {
                "player": agent.name,
                "turn_number": len(self.history.turns) + 1,
                "card_type": selected_card.card_type.value.split('_')[0].lower(),
                "card_id": selected_card.id,
                "success": True
            }
            
            # After recording a successful turn
            if turn_data["success"]:
                self.history.add_turn(
                    turn_number=turn_data["turn_number"],
                    player_name=turn_data["player"],
                    thought_process=scratch_pad,
                    selected_card=selected_card,
                    contract_state=self.contract.current_code,
                    variables=self.contract.variables.copy()
                )
            
        except ValueError as e:
            # Handle parsing errors specifically
            turn_data = {
                "player": agent.name,
                "turn_number": len(self.history.turns) + 1,
                "error": str(e),
                "success": False,
                "card_type": None,
                "card_id": None
            }
            
        except Exception as e:
            # Handle other errors
            turn_data = {
                "player": agent.name,
                "turn_number": len(self.history.turns) + 1,
                "error": str(e),
                "success": False,
                "card_type": None,
                "card_id": None
            }
        
        # Always record the turn data
        if turn_data:
            self._game_result["turn_history"].append(turn_data)
            
            # Add to game history if it was a failed turn
            if not turn_data["success"]:
                self.history.add_turn(
                    turn_number=turn_data["turn_number"],
                    player_name=turn_data["player"],
                    thought_process=f"Invalid move - {turn_data['error']}",
                    selected_card=None,
                    contract_state=self.contract.current_code,
                    variables=self.contract.variables.copy()
                )
        
        if len(self.history.turns) >= self.config.max_turns:
            self.game_over = True
            self._game_result["victory_condition"] = "Game ended due to max turns reached"
            return False
        
        self.check_victory_conditions()
        
        # Update profiles if game is over
        if self.game_over:
            self._update_agent_profiles()
        
        # Switch players if game isn't over
        if not self.game_over:
            self.current_player = 'agent2' if self.current_player == 'agent1' else 'agent1'
        
        return not self.game_over

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
            # Split on SELECTED CARD: and get the last instance
            parts = response.split("SELECTED CARD:")
            if len(parts) < 2:
                raise ValueError("No 'SELECTED CARD:' section found in response")
            
            scratch_pad = parts[0].replace("SCRATCH PAD:", "").strip()
            card_text = parts[-1].strip()
            
            # Look for first number in the response
            numbers = [int(word) for word in card_text.split() if word.isdigit()]
            if not numbers:
                raise ValueError("No valid card number found in selection")
            
            card_number = numbers[0]
            
            # Validate card number range immediately
            if not (1 <= card_number <= len(self.available_cards)):
                raise ValueError(f"Card number {card_number} out of valid range")
            
            return scratch_pad, card_number
            
        except Exception as e:
            # Convert all exceptions to ValueError with clear message
            raise ValueError(f"Invalid response format: {str(e)}")

    def _update_agent_profiles(self):
        """Update profiles for both agents when game ends"""
        game_result = {
            "winner": self.winner or "Draw",
            "total_turns": len(self.history.turns),
            "victory_condition": (
                f"{self.winner} achieved victory condition" 
                if self.winner 
                else "Game ended in draw"
            ),
            "turn_history": self._game_result["turn_history"]
        }
        
        # Update both agents' profiles
        for agent in self.agents.values():
            if hasattr(agent, 'update_profile'):
                agent.update_profile(game_result)

    def check_victory_conditions(self) -> None:
        """Check if either player has achieved their victory condition"""
        for player_id, agent in self.agents.items():
            if self.contract.check_victory_condition(agent.victory_condition):
                self.game_over = True
                self.winner = agent.name
                self._game_result["winner"] = self.winner
                self._game_result["victory_condition"] = f"{self.winner} achieved victory condition"
                break
        
        # Add this to handle max turns reached
        if not self.winner and len(self.history.turns) >= self.config.max_turns:
            self.game_over = True
            self._game_result["victory_condition"] = "Game ended due to max turns reached"