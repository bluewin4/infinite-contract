from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
from ..agents.base_agent import BaseAgent

@dataclass
class AgentInfo:
    name: str
    model_type: str
    victory_condition: str
    parameters: Dict[str, any]

@dataclass
class GameMetadata:
    start_time: datetime
    end_time: Optional[datetime] = None
    winner: Optional[str] = None
    total_turns: int = 0
    agents: Dict[str, AgentInfo] = None

@dataclass
class TurnRecord:
    turn_number: int
    player_name: str
    thought_process: str
    selected_card: int
    contract_state: List[str]
    variables: Dict[str, int]
    timestamp: datetime = datetime.now()

class GameHistory:
    def __init__(self):
        self.turns: List[TurnRecord] = []
        self.metadata: GameMetadata = None
        
    def initialize_game(self, agents: Dict[str, 'BaseAgent']):
        """Initialize game metadata with agent information"""
        agent_info = {}
        for name, agent in agents.items():
            agent_info[name] = AgentInfo(
                name=agent.name,
                model_type=getattr(agent, 'model', 'simple'),
                victory_condition=agent.victory_condition,
                parameters={
                    'temperature': getattr(agent, 'temperature', None),
                    'max_tokens': getattr(agent, 'max_tokens', None),
                    **getattr(agent, 'model_kwargs', {})
                }
            )
        
        self.metadata = GameMetadata(
            start_time=datetime.now(),
            agents=agent_info
        )
    
    def finalize_game(self, winner: Optional[str] = None):
        """Record game completion details"""
        if self.metadata:
            self.metadata.end_time = datetime.now()
            self.metadata.winner = winner
            self.metadata.total_turns = len(self.turns)
    
    def add_turn(self, 
                turn_number: int,
                player_name: str,
                thought_process: str,
                selected_card: int,
                contract_state: List[str],
                variables: Dict[str, int]):
        # Existing validation
        expected_turn = len(self.turns) + 1
        if turn_number != expected_turn:
            raise ValueError(f"Invalid turn number. Expected {expected_turn}, got {turn_number}")
        
        record = TurnRecord(
            turn_number=turn_number,
            player_name=player_name,
            thought_process=thought_process,
            selected_card=selected_card,
            contract_state=contract_state.copy(),
            variables=variables.copy(),
            timestamp=datetime.now()
        )
        self.turns.append(record)
    
    def get_player_turns(self, player_name: str) -> List[TurnRecord]:
        return [turn for turn in self.turns if turn.player_name == player_name]
    
    def get_turn(self, turn_number: int) -> Optional[TurnRecord]:
        return next((turn for turn in self.turns if turn.turn_number == turn_number), None)
    
    def get_recent_turns(self, window: int) -> List[TurnRecord]:
        """Get the most recent n turns from history"""
        return self.turns[-window:] if self.turns else []
    
    def export_game_data(self) -> Dict:
        """Export game data in a serializable format"""
        return {
            'metadata': {
                'start_time': self.metadata.start_time.isoformat(),
                'end_time': self.metadata.end_time.isoformat() if self.metadata.end_time else None,
                'winner': self.metadata.winner,
                'total_turns': self.metadata.total_turns,
                'agents': {
                    name: {
                        'name': info.name,
                        'model_type': info.model_type,
                        'victory_condition': info.victory_condition,
                        'parameters': info.parameters
                    } for name, info in self.metadata.agents.items()
                }
            },
            'turns': [
                {
                    'turn_number': turn.turn_number,
                    'player_name': turn.player_name,
                    'thought_process': turn.thought_process,
                    'selected_card': turn.selected_card,
                    'contract_state': turn.contract_state,
                    'variables': turn.variables,
                    'timestamp': turn.timestamp.isoformat()
                } for turn in self.turns
            ]
        }