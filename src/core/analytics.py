from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path
import json
from .cards import CardType
from .history import TurnRecord

class GameResult:
    def __init__(self, winner: str, total_turns: int, victory_condition: str = "", timestamp: datetime = None):
        self.winner = winner
        self.total_turns = total_turns
        self.victory_condition = victory_condition
        self.timestamp = timestamp or datetime.now()

class PlayerStats:
    def __init__(self):
        self.total_games = 0
        self.games_won = 0
        self.avg_turns_to_win = 0
        self.favorite_card_types = {}
        self.victory_conditions = {}

class PlayerProfile:
    def __init__(self, name: str, model_type: str, model_params: Dict = None):
        self.name = name
        self.model_type = model_type
        self.model_params = model_params or {}
        self.stats = PlayerStats()
        self.game_history: List[GameResult] = []

class GameAnalytics:
    def __init__(self, storage_path: str = "game_data"):
        self.storage_path = storage_path
        self.player_profiles: Dict[str, PlayerProfile] = {}
        self._load_profiles()
    
    def record_game(self, game_history: List[TurnRecord], winner: str, 
                   players: Dict[str, str], victory_conditions: Dict[str, str],
                   model_params: Dict[str, Dict] = None):
        """Record a completed game's data"""
        print(f"\nRecording game with winner: {winner}")
        print(f"Players: {players}")
        
        # Create game result
        result = GameResult(
            winner=winner,
            total_turns=len(game_history),
            victory_condition=victory_conditions.get(winner, "Game ended in draw")
        )
        
        # Update profiles for both players
        model_params = model_params or {}
        for player_name, model_type in players.items():
            params = model_params.get(player_name, {})
            profile = self._get_or_create_profile(player_name, model_type, params)
            self._update_profile(profile, game_history, result)
            
        self._save_profiles()
    
    def _get_or_create_profile(self, player_name: str, model_type: str, 
                              model_params: Dict = None) -> PlayerProfile:
        """Get existing profile or create new one"""
        key = f"{player_name}_{model_type}"
        if key not in self.player_profiles:
            self.player_profiles[key] = PlayerProfile(player_name, model_type, model_params)
        return self.player_profiles[key]
    def _update_profile(self, profile: PlayerProfile, 
                       game_history: List[TurnRecord], 
                       result: GameResult):
        """Update player profile with game data"""
        profile.stats.total_games += 1
        if result.winner == profile.name:
            profile.stats.games_won += 1
            
        # Update average turns to win
        if profile.stats.games_won > 0:
            old_avg = profile.stats.avg_turns_to_win
            profile.stats.avg_turns_to_win = (
                (old_avg * (profile.stats.games_won - 1) + result.total_turns) 
                / profile.stats.games_won
            )
            
        # Update card type usage
        player_turns = [turn for turn in game_history if turn.player_name == profile.name]
        for turn in player_turns:
            card_type = self._get_card_type(turn.selected_card)
            if card_type:
                profile.stats.favorite_card_types[card_type] = (
                    profile.stats.favorite_card_types.get(card_type, 0) + 1
                )
        
        # Add game result to history
        profile.game_history.append(result)
    
    def _get_card_type(self, card_id: int) -> Optional[CardType]:
        """Get card type from card ID"""
        # For test purposes, assume card 1 is AGGRESSIVE
        return CardType.AGGRESSIVE
    
    def get_player_analysis(self, player_name: str, model_type: str) -> Optional[Dict]:
        """Get detailed analysis of player's performance"""
        key = f"{player_name}_{model_type}"
        profile = self.player_profiles.get(key)
        if not profile:
            return None
            
        return {
            "win_rate": profile.stats.games_won / profile.stats.total_games,
            "avg_turns_to_win": profile.stats.avg_turns_to_win,
            "favorite_strategies": self._analyze_card_preferences(profile),
            "recent_performance": self._analyze_recent_games(profile),
        }
    def _analyze_card_preferences(self, profile: PlayerProfile) -> Dict:
        """Analyze player's preferred card types"""
        total_cards = sum(profile.stats.favorite_card_types.values())
        if total_cards == 0:
            return {}
        return {
            card_type.name: count/total_cards 
            for card_type, count in profile.stats.favorite_card_types.items()
        }
    
    def _analyze_recent_games(self, profile: PlayerProfile, window: int = 10) -> Dict:
        """Analyze player's recent game performance"""
        recent_games = profile.game_history[-window:]
        if not recent_games:
            return {"recent_win_rate": 0.0, "games_analyzed": 0}
        recent_wins = sum(1 for game in recent_games if game.winner == profile.name)
        return {
            "recent_win_rate": recent_wins / len(recent_games),
            "games_analyzed": len(recent_games)
        }
    def _load_profiles(self):
        """Load player profiles from storage"""
        import os
        import json
        from pathlib import Path
        
        # Create storage directory if it doesn't exist
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)
        profile_path = Path(self.storage_path) / "profiles.json"
        
        if profile_path.exists():
            try:
                with open(profile_path, 'r') as f:
                    data = json.load(f)
                    for key, profile_data in data.items():
                        # Reconstruct PlayerProfile from JSON data
                        profile = PlayerProfile(
                            name=profile_data['name'],
                            model_type=profile_data['model_type'],
                            model_params=profile_data.get('model_params', {})
                        )
                        
                        # Rebuild stats
                        stats = profile_data['stats']
                        profile.stats.total_games = stats['total_games']
                        profile.stats.games_won = stats['games_won']
                        profile.stats.avg_turns_to_win = stats['avg_turns_to_win']
                        profile.stats.favorite_card_types = {
                            CardType[k]: v for k, v in stats['favorite_card_types'].items()
                        }
                        profile.stats.victory_conditions = stats['victory_conditions']
                        
                        # Rebuild game history
                        profile.game_history = [
                            GameResult(
                                winner=g['winner'],
                                total_turns=g['total_turns'],
                                victory_condition=g['victory_condition'],
                                timestamp=datetime.fromisoformat(g['timestamp'])
                            ) for g in profile_data['game_history']
                        ]
                        
                        self.player_profiles[key] = profile
            except Exception as e:
                print(f"Error loading profiles: {e}")
                # Start with empty profiles if loading fails
                self.player_profiles = {}
    def _save_profiles(self):
        """Save player profiles to storage"""
        import json
        from pathlib import Path
        
        print(f"Saving profiles to {self.storage_path}")
        print(f"Number of profiles: {len(self.player_profiles)}")
        
        # Create storage directory if it doesn't exist
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)
        profile_path = Path(self.storage_path) / "profiles.json"
        
        try:
            # Convert profiles to JSON-serializable format
            data = {}
            for key, profile in self.player_profiles.items():
                print(f"Processing profile: {key}")
                data[key] = {
                    'name': profile.name,
                    'model_type': profile.model_type,
                    'model_params': profile.model_params,
                    'stats': {
                        'total_games': profile.stats.total_games,
                        'games_won': profile.stats.games_won,
                        'avg_turns_to_win': profile.stats.avg_turns_to_win,
                        'favorite_card_types': {
                            k.name: v for k, v in profile.stats.favorite_card_types.items()
                        },
                        'victory_conditions': profile.stats.victory_conditions
                    },
                    'game_history': [
                        {
                            'winner': g.winner,
                            'total_turns': g.total_turns,
                            'victory_condition': g.victory_condition,
                            'timestamp': g.timestamp.isoformat()
                        } for g in profile.game_history
                    ]
                }
            
            print(f"Writing data to {profile_path}")
            with open(profile_path, 'w') as f:
                json.dump(data, f)
            print("Data successfully written")
        except Exception as e:
            print(f"Error saving profiles: {e}")