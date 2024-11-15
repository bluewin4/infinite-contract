# Game Profile Tracking System

## Overview
The profile tracking system maintains persistent statistics and history for each AI agent across multiple games. This system consists of three main components:

1. Profile Initialization
2. Game Result Recording
3. Profile Updates

## Flow of Information

### 1. Profile Initialization
- Each agent has a unique profile identified by: name + personality hash + model + temperature
- Profiles are stored in `storage/profiles.json`
- New profiles are initialized with:
  - Basic stats (total_games, games_won, win_rate)
  - Card usage statistics
  - Empty game history
  - Personality traits (if applicable)

### 2. Game Result Recording
During each game:
- Turn history is recorded in `_game_result["turn_history"]`
- Each turn records:
  - Player name
  - Card type used
  - Success/failure
  - Game state
- Victory conditions and final state are tracked

### 3. Profile Updates
Profile updates occur exactly once per game when either:
- Victory conditions are met
- Maximum turns are reached

The update process:
1. `InfiniteContractGame._update_agent_profiles()` creates game result
2. `LMAgent.update_profile()` receives game result and updates:
   - Increments total_games
   - Updates win statistics
   - Records card usage
   - Appends to game history

## Key Design Decisions
1. Single update per game to prevent duplicate statistics
2. Persistent storage across game sessions
3. Comprehensive tracking of:
   - Game outcomes
   - Card usage patterns
   - Strategic decisions
   - Victory conditions

## Testing
The system is verified through tests that ensure:
1. Correct game counting
2. Proper card usage tracking
3. Accurate victory recording
4. Personality trait persistence 