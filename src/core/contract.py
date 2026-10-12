from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import ast
from .cards import Card

@dataclass
class ContractState:
    code: List[str]
    variables: Dict[str, Any]
    execution_order: List[int]

class CodeContract:
    def __init__(self):
        self.current_code: List[str] = []
        self.variables: Dict[str, Any] = {'x': 1, 'y': 1, 'z': 1}
        self.execution_order: List[int] = []
        self._state_history: List[ContractState] = []
        
    def add_line(self, code: str) -> bool:
        """Add a new line of code to the contract"""
        if code.startswith("__contract__"):
            return self._handle_special_command(code)
        else:
            return self._add_normal_line(code)

    def _add_normal_line(self, code: str) -> bool:
        """Add a regular code line to the contract"""
        try:
            # Save current state
            self._save_state()
            
            # Add line
            self.current_code.append(code)
            self.execution_order.append(len(self.current_code) - 1)
            
            # Execute contract
            if not self._execute_contract():
                self._restore_state()
                return False
                
            return True
            
        except Exception:
            self._restore_state()
            return False

    def _handle_special_command(self, code: str) -> bool:
        """Handle special contract management commands"""
        try:
            if code == "__contract__.pop()":
                return self._remove_last_line()
            elif code == "__contract__.clean()":
                return self._clean_inactive_lines()
            elif code == "__contract__.optimize()":
                return self._optimize_execution_order()
            elif code == "__contract__.clear()":
                return self._clear_all_lines()
            elif code == "__contract__.invert()":
                return self._invert_execution_order()
            elif code == "__contract__.remove(x)":
                return self._remove_line(self.variables['x'])
            elif code == "__contract__.remove_first()":
                return bool(self.execution_order) and self._remove_line(self.execution_order[0])
            elif code == "__contract__.duplicate_last()":
                return bool(self.current_code) and self._add_normal_line(self.current_code[-1])
            elif code == "__contract__.last_to_top()":
                return self._move_last_to_top()
            return False
        except Exception:
            return False

    def _remove_last_line(self) -> bool:
        if not self.current_code:
            return False
        self._save_state()
        self.current_code.pop()
        self.execution_order = [i for i in self.execution_order if i < len(self.current_code)]
        return self._execute_contract()

    def _clean_inactive_lines(self) -> bool:
        self._save_state()
        active_indices = [i for i in range(len(self.current_code)) if i in self.execution_order]
        new_index = {old: new for new, old in enumerate(active_indices)}
        
        self.current_code = [self.current_code[i] for i in active_indices]
        self.execution_order = [new_index[i] for i in self.execution_order if i in new_index]
        return self._execute_contract()

    def _optimize_execution_order(self) -> bool:
        self._save_state()
        self.execution_order = list(range(len(self.current_code)))
        return self._execute_contract()

    def _execute_contract(self) -> bool:
        """Execute the contract safely"""
        # Reset variables to initial state before executing
        self.variables = {'x': 1, 'y': 1, 'z': 1}
        temp_vars = self.variables.copy()
        
        try:
            # Execute each line in order
            for idx in self.execution_order:
                if idx < len(self.current_code):
                    exec(self.current_code[idx], {"__builtins__": {}}, temp_vars)
            
            self.variables = temp_vars
            return True
            
        except Exception:
            return False
            
    def _save_state(self):
        """Save current state"""
        self._state_history.append({
            'code': self.current_code.copy(),
            'variables': self.variables.copy(),
            'execution_order': self.execution_order.copy()
        })
        
    def _restore_state(self):
        """Restore last valid state"""
        if self._state_history:
            state = self._state_history.pop()
            self.current_code = state['code']
            self.variables = state['variables']
            self.execution_order = state['execution_order']

    def apply_card(self, card: 'Card') -> None:
        """Apply a card's code to the contract"""
        self.add_line(card.code)

    def check_victory_condition(self, condition: str) -> bool:
        """Check if the victory condition is met"""
        try:
            # Create a copy of variables for safe evaluation
            vars_copy = self.variables.copy()
            # Handle greater than or equal conditions
            if '>=' in condition:
                var, target = condition.split('>=')
                var = var.strip()
                target = int(target.strip())
                return vars_copy[var] >= target
            # Handle less than or equal conditions
            elif '<=' in condition:
                var, target = condition.split('<=')
                var = var.strip()
                target = int(target.strip())
                return vars_copy[var] <= target
            # Handle equality conditions
            elif '==' in condition:
                var, target = condition.split('==')
                var = var.strip()
                target = int(target.strip())
                return vars_copy[var] == target
            return False
        except Exception:
            return False

    def _clear_all_lines(self) -> bool:
        """Clear all lines from the contract"""
        self._save_state()
        self.current_code = []
        self.execution_order = []
        return self._execute_contract()

    def _invert_execution_order(self) -> bool:
        """Invert the execution order of all lines"""
        self._save_state()
        self.execution_order = list(reversed(self.execution_order))
        return self._execute_contract()

    def _move_last_to_top(self) -> bool:
        """Move the last line in the execution order to the front"""
        if len(self.execution_order) < 2:
            return False
        self._save_state()
        self.execution_order = [self.execution_order[-1]] + self.execution_order[:-1]
        return self._execute_contract()

    def _remove_line(self, index: int) -> bool:
        """Remove a specific line from the contract by index"""
        if not self.current_code or index < 0 or index >= len(self.current_code):
            return False
        
        self._save_state()
        # Remove the line
        self.current_code.pop(index)
        # Update execution order by removing the index and shifting remaining indices
        self.execution_order = [i if i < index else i - 1 for i in self.execution_order if i != index]
        return self._execute_contract()