from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class TurnRecord:
    turn_number: int
    player_name: str
    thought_process: str
    selected_card: int
    contract_state: List[str]
    variables: Dict[str, int]
    card_name: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

class GameHistory:
    def __init__(self):
        self.turns: List[TurnRecord] = []
        
    def add_turn(self, 
                 turn_number: int,
                 player_name: str,
                 thought_process: str,
                 selected_card: int,
                 contract_state: List[str],
                 variables: Dict[str, int],
                 card_name: Optional[str] = None):
        record = TurnRecord(
            turn_number=turn_number,
            player_name=player_name,
            thought_process=thought_process,
            selected_card=selected_card,
            contract_state=contract_state.copy(),
            variables=variables.copy(),
            card_name=card_name
        )
        self.turns.append(record)
    
    def get_player_turns(self, player_name: str) -> List[TurnRecord]:
        return [turn for turn in self.turns if turn.player_name == player_name]
    
    def get_turn(self, turn_number: int) -> Optional[TurnRecord]:
        return next((turn for turn in self.turns if turn.turn_number == turn_number), None)
    
    def get_recent_turns(self, window: int) -> List[TurnRecord]:
        """Get the most recent n turns from history"""
        return self.turns[-window:] if self.turns else []