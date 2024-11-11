import pytest
from src.core.contract import CodeContract, ContractState

def test_basic_contract_execution():
    contract = CodeContract()
    
    # Test simple line addition
    assert contract.add_line("x = x + 1")
    assert contract.variables['x'] == 2
    
    # Test multiple lines
    assert contract.add_line("y = y * 2")
    assert contract.variables == {'x': 2, 'y': 2, 'z': 1}

def test_invalid_code():
    contract = CodeContract()
    
    # Test syntax error
    assert not contract.add_line("x = x +")
    assert contract.variables['x'] == 1  # Should maintain initial state
    
    # Test undefined variable
    assert not contract.add_line("w = 1")
    assert 'w' not in contract.variables
    
    # Test forbidden operations
    assert not contract.add_line("import os")
    assert not contract.add_line("__import__('os')")

def test_state_management():
    contract = CodeContract()
    
    # Test state saving and restoration
    contract.add_line("x = x + 1")
    initial_state = {
        'code': contract.current_code.copy(),
        'variables': contract.variables.copy(),
        'execution_order': contract.execution_order.copy()
    }
    
    # Add invalid line
    assert not contract.add_line("invalid code")
    
    # Check state was restored
    assert contract.current_code == initial_state['code']
    assert contract.variables == initial_state['variables']
    assert contract.execution_order == initial_state['execution_order']

def test_execution_order():
    contract = CodeContract()
    
    # Test normal execution order
    contract.add_line("x = x + 1")  # x: 1 -> 2
    contract.add_line("y = x")      # y: 1 -> 2
    contract.add_line("x = x * 2")  # x: 2 -> 4
    
    assert contract.variables == {'x': 4, 'y': 2, 'z': 1}
    
    # Test execution order manipulation
    contract._invert_execution_order()
    # Should now execute: x*2, then y=x, then x+1
    assert contract.variables == {'x': 3, 'y': 2, 'z': 1}

def test_victory_conditions():
    contract = CodeContract()
    
    # Test various victory condition formats
    contract.add_line("x = 5")
    
    assert contract.check_victory_condition("x >= 3")
    assert contract.check_victory_condition("x == 5")
    assert not contract.check_victory_condition("x <= 3")
    assert not contract.check_victory_condition("x == 6")
    
    # Test invalid conditions
    assert not contract.check_victory_condition("invalid condition")
    assert not contract.check_victory_condition("w >= 5")  # undefined variable

def test_special_commands():
    contract = CodeContract()
    
    # Test pop command
    contract.add_line("x = x + 1")
    contract.add_line("y = y + 1")
    assert contract._handle_special_command("__contract__.pop()")
    assert len(contract.current_code) == 1
    
    # Test clean command
    contract = CodeContract()
    contract.add_line("x = x + 1")
    contract.execution_order = []  # Make first line inactive
    assert contract._handle_special_command("__contract__.clean()")
    assert len(contract.current_code) == 0
    
    # Test optimize command
    contract = CodeContract()
    contract.add_line("x = x + 1")
    contract.add_line("y = y + 1")
    contract.execution_order = [1, 0]  # Reverse order
    assert contract._handle_special_command("__contract__.optimize()")
    assert contract.execution_order == [0, 1]

def test_variable_isolation():
    contract = CodeContract()
    
    # Test that variables are properly isolated
    assert not contract.add_line("import os")
    assert not contract.add_line("__builtins__['open']('file.txt')")
    assert not contract.add_line("eval('1+1')")
    assert not contract.add_line("globals()['x'] = 100")
    
    # Test that only allowed variables can be modified
    assert contract.add_line("x = 5")
    assert not contract.add_line("new_var = 10") 