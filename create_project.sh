#!/bin/bash

# Create main project directory
mkdir -p infinite_contract_game/src/core
mkdir -p infinite_contract_game/src/agents
mkdir -p infinite_contract_game/src/validation
mkdir -p infinite_contract_game/src/execution
mkdir -p infinite_contract_game/src/storage
mkdir -p infinite_contract_game/src/api

mkdir -p infinite_contract_game/tests/unit
mkdir -p infinite_contract_game/tests/integration
mkdir -p infinite_contract_game/tests/performance

mkdir -p infinite_contract_game/docs/api
mkdir -p infinite_contract_game/docs/architecture
mkdir -p infinite_contract_game/docs/examples

mkdir -p infinite_contract_game/config
mkdir -p infinite_contract_game/logs

# Create core module files
touch infinite_contract_game/src/core/__init__.py
touch infinite_contract_game/src/core/contract.py
touch infinite_contract_game/src/core/game.py
touch infinite_contract_game/src/core/history.py
touch infinite_contract_game/src/core/metrics.py

# Create agent-related files
touch infinite_contract_game/src/agents/__init__.py
touch infinite_contract_game/src/agents/base_agent.py
touch infinite_contract_game/src/agents/memory.py
touch infinite_contract_game/src/agents/strategy.py

# Create validation files
touch infinite_contract_game/src/validation/__init__.py
touch infinite_contract_game/src/validation/move_validator.py
touch infinite_contract_game/src/validation/syntax_checker.py
touch infinite_contract_game/src/validation/complexity_calculator.py

# Create execution files
touch infinite_contract_game/src/execution/__init__.py
touch infinite_contract_game/src/execution/sandbox.py
touch infinite_contract_game/src/execution/interpreter.py
touch infinite_contract_game/src/execution/safety_manager.py

# Create storage files
touch infinite_contract_game/src/storage/__init__.py
touch infinite_contract_game/src/storage/persistence.py
touch infinite_contract_game/src/storage/serialization.py

# Create API files
touch infinite_contract_game/src/api/__init__.py
touch infinite_contract_game/src/api/endpoints.py
touch infinite_contract_game/src/api/schemas.py

# Create config files
touch infinite_contract_game/config/default_config.yaml
touch infinite_contract_game/config/logging_config.yaml

# Create main entry point
touch infinite_contract_game/main.py

# Create setup files
touch infinite_contract_game/{
    setup.py,
    requirements.txt,
    README.md,
    .gitignore


echo "Project structure created successfully!" 