import re
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

from .contract import CodeContract
from .history import GameHistory
from ..agents.base_agent import BaseAgent
from .cards import CardLibrary, CardType, Card

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
        self.winner: Optional[str] = None  # agent name, "draw", or None while playing
        
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
        agent = self.agents[self.current_player]
        
        # Create and send prompt
        prompt = self.create_turn_prompt()
        response = agent.get_response(prompt)
        
        # Extract selected card and thought process
        selected_card = self._extract_selected_card(response)
        
        scratch_pad = self._extract_scratch_pad(response)
        if scratch_pad:
            agent.add_strategy_note(scratch_pad)
        
        # Apply the selected card
        card = None
        if selected_card is not None:
            card = self.available_cards[selected_card - 1]
            self.contract.apply_card(card)
            
        # Record the turn in history
        self.history.add_turn(
            turn_number=len(self.history.turns) + 1,
            player_name=agent.name,
            thought_process=response,
            selected_card=selected_card,
            contract_state=self.contract.current_code,
            variables=self.contract.variables,
            card_name=card.name if card else None
        )
        
        # Check victory conditions; if one move satisfies both, it's a draw
        winners = [a.name for a in self.agents.values()
                   if self.contract.check_victory_condition(a.victory_condition)]
        if len(winners) > 1:
            self.winner = "draw"
            print("\nBoth victory conditions met - it's a draw!")
            return False
        if winners:
            self.winner = winners[0]
            print(f"\n{winners[0]} has won!")
            return False
        
        # Switch players
        self._switch_players()
        return True

    def _extract_selected_card(self, response: str) -> Optional[int]:
        """Extract the selected card number from the response"""
        match = re.search(r"SELECTED CARD:\s*\[?\s*(\d+)", response)
        if match:
            card_number = int(match.group(1))
            if 1 <= card_number <= len(self.available_cards):
                return card_number
        return None

    def _extract_scratch_pad(self, response: str) -> str:
        """Extract the scratch pad text that precedes the selected card"""
        scratch_pad = response.split("SELECTED CARD:")[0]
        return scratch_pad.replace("SCRATCH PAD:", "").strip()

    def _switch_players(self):
        """Switch to the next player"""
        self.current_player = 'agent2' if self.current_player == 'agent1' else 'agent1'

    def _format_contract(self) -> str:
        return "\n".join(f"{i}: {line}" for i, line in enumerate(self.contract.current_code))

    def _format_variables(self) -> str:
        return "\n".join(f"{k}: {v}" for k, v in self.contract.variables.items())

    def _format_history(self, history) -> str:
        return "\n".join(
            f"Turn {turn.turn_number}: {turn.player_name} played {turn.card_name or 'no card (invalid move)'} - Variables: {turn.variables}"
            for turn in history
        )

    def _format_cards(self) -> str:
        return "\n".join(f"{i+1}. {card.name}: {card.description}" 
                        for i, card in enumerate(self.available_cards))

    def _format_notes(self, notes: List[str]) -> str:
        return "\n".join(notes[-self.config.memory_window:])

    def _get_available_cards(self) -> List[Card]:
        """Get available cards for the current player"""
        agent = self.agents[self.current_player]
        # Get allowed card types based on the player's target variable
        allowed_types = self.config.get_allowed_cards(agent.target_var)
        
        all_cards = []
        for card_type in allowed_types:
            all_cards.extend(self.config.card_library.get_cards_by_type(card_type))
            
        # Randomly select cards_per_turn number of cards
        import random
        return random.sample(all_cards, min(len(all_cards), self.config.cards_per_turn))