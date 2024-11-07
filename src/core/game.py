from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .contract import CodeContract
from .history import GameHistory
from ..agents.base_agent import BaseAgent
from .cards import CardLibrary, CardType, Card

@dataclass
class GameConfig:
    max_turns: int = 50
    memory_window: int = 5
    victory_conditions: Dict[str, str] = None
    card_library: CardLibrary = None
    allowed_card_types: List[CardType] = None
    cards_per_turn: int = 3  # Number of cards to offer each turn

class InfiniteContractGame:
    def __init__(self, agent1: BaseAgent, agent2: BaseAgent, config: GameConfig):
        self.contract = CodeContract()
        self.history = GameHistory()
        self.agents = {'agent1': agent1, 'agent2': agent2}
        self.config = config
        self.current_player = 'agent1'
        
        # Set victory conditions
        agent1.victory_condition = config.victory_conditions['agent1']
        agent2.victory_condition = config.victory_conditions['agent2']
        
    def create_turn_prompt(self) -> str:
        """Create the prompt for current turn"""
        agent = self.agents[self.current_player]
        recent_history = self.history.get_recent_turns(self.config.memory_window)
        
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
        agent = self.agents[self.current_player]
        
        # Create and send prompt
        prompt = self.create_turn_prompt()
        response = agent.get_response(prompt)
        
        # Process response
        success = self._process_response(response)
        
        # Switch players if successful
        if success:
            self.current_player = 'agent2' if self.current_player == 'agent1' else 'agent1'
            
        return not self._check_victory()
        
    def _process_response(self, response: str) -> bool:
        """Process agent's response"""
        try:
            # Parse response
            scratch_pad, card_number = self._parse_response(response)
            
            # Get selected card from available cards
            available_cards = self._get_available_cards()
            if not (1 <= card_number <= len(available_cards)):
                return False
            
            card = available_cards[card_number - 1]
            
            # Save variables state
            vars_before = self.contract.variables.copy()
            
            # Execute card
            success = self.contract.add_line(card.code)
            
            # Record turn
            self.history.add_turn(
                player_id=self.current_player,
                move_card=card,
                variables_before=vars_before,
                variables_after=self.contract.variables,
                scratch_pad=scratch_pad,
                success=success
            )
            
            return success
            
        except Exception as e:
            print(f"Error processing response: {e}")  # Add debugging
            return False
            
    def _check_victory(self) -> bool:
        """Check if current player has won"""
        condition = self.config.victory_conditions[self.current_player]
        try:
            return eval(condition, {"__builtins__": {}}, self.contract.variables)
        except Exception:
            return False

    def _format_contract(self) -> str:
        return "\n".join(f"{i}: {line}" for i, line in enumerate(self.contract.current_code))

    def _format_variables(self) -> str:
        return "\n".join(f"{k}: {v}" for k, v in self.contract.variables.items())

    def _format_history(self, history) -> str:
        return "\n".join(
            f"Turn {turn.turn_number}: Player {turn.player_id} played {turn.move_card} - Variables: {turn.variables_after}"
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