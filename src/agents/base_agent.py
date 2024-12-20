from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAgent(ABC):
    """Base class for game agents"""
    
    def __init__(self, name: str, victory_condition: str = "", target_var: str = "x"):
        self.name = name
        self.victory_condition = victory_condition
        self.target_var = target_var
        self.strategy_notes: List[str] = []

    @abstractmethod
    def get_response(self, prompt: str) -> str:
        """Generate a response to the game prompt"""
        pass

    def update_memory(self, turn_result: Dict[str, Any]):
        """Update agent's memory with turn results"""
        if 'scratch_pad' in turn_result:
            self.strategy_notes.append(turn_result['scratch_pad'])

    def add_strategy_note(self, note: str):
        """Add a note to agent's strategy notes"""
        self.strategy_notes.append(note)

class SimpleAgent(BaseAgent):
    """A simple agent that makes random valid moves"""
    
    def get_response(self, prompt: str) -> str:
        """Generate a simple response"""
        # For demonstration, always tries to increment x
        scratch_pad = "Planning to increment variable x"
        move_type = "add_line"
        content = "x += 1"
        
        return f"""
SCRATCH PAD:
{scratch_pad}

MOVE TYPE:
{move_type}

CONTENT:
{content}
""" 