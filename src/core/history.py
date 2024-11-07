from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class TurnRecord:
    turn_number: int
    player_id: str
    timestamp: datetime
    move_card: str
    variables_before: Dict[str, Any]
    variables_after: Dict[str, Any]
    scratch_pad: str
    success: bool

class GameHistory:
    def __init__(self):
        self.turns: List[TurnRecord] = []
        
    def add_turn(self, 
                 player_id: str,
                 move_card: str,
                 variables_before: Dict[str, Any],
                 variables_after: Dict[str, Any],
                 scratch_pad: str,
                 success: bool):
        """Add a turn to history"""
        turn = TurnRecord(
            turn_number=len(self.turns) + 1,
            player_id=player_id,
            timestamp=datetime.now(),
            move_card=move_card,
            variables_before=variables_before,
            variables_after=variables_after,
            scratch_pad=scratch_pad,
            success=success
        )
        self.turns.append(turn)
        
    def get_recent_turns(self, window_size: int = 5) -> List[TurnRecord]:
        """Get most recent turns"""
        return self.turns[-window_size:] 