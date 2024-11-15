from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from litellm import completion
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from pathlib import Path
import hashlib

class LMAgent(BaseAgent):
    def __init__(self, 
                 name: str, 
                 model: str, 
                 victory_condition: str, 
                 personality: Optional[str] = None,
                 system_prompt: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 500,
                 testing: bool = False,
                 **model_kwargs):
        # Load environment variables at initialization
        load_dotenv()
        
        # Skip API key validation if in testing mode
        if not testing:
            self._check_api_keys(model)
            
        super().__init__(name, victory_condition)
        self.model = model
        self.personality = personality
        self.system_prompt = system_prompt or self._create_system_prompt()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model_kwargs = model_kwargs
        
        # Always initialize profile, even in testing mode
        self._initialize_profile()

    def _initialize_profile(self):
        """Initialize or load the agent's profile"""
        storage_path = Path(os.getenv("STORAGE_PATH", "storage"))
        profiles_path = storage_path / "profiles.json"
        
        # Create storage directory if it doesn't exist
        storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load or create profiles file
        if profiles_path.exists():
            with open(profiles_path) as f:
                profiles = json.load(f)
        else:
            profiles = {}
        
        # Create unique agent ID including personality hash
        agent_id = self._generate_agent_id()
        
        # Create agent profile if it doesn't exist
        if agent_id not in profiles:
            profiles[agent_id] = {
                "name": self.name,
                "personality": self.personality,
                "model_type": "lmagent",
                "model_params": {
                    "model": self.model,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                },
                "stats": {
                    "total_games": 0,
                    "games_won": 0,
                    "win_rate": 0.0,
                    "avg_turns_to_win": 0,
                    "favorite_card_types": {},
                    "victory_conditions": [],
                    "personality_traits": {
                        "aggression": 0.0,
                        "defensiveness": 0.0,
                        "strategy_depth": 0.0,
                        "adaptability": 0.0
                    },
                    "card_type_stats": {
                        "aggressive": 0,
                        "defensive": 0,
                        "strategic": 0,
                        "utility": 0,
                        "cards_per_game": []
                    }
                },
                "game_history": []
            }
        
        # Always save the profile
        with open(profiles_path, 'w') as f:
            json.dump(profiles, f, indent=4)
        
        return profiles[agent_id]

    def _check_api_keys(self, model: str):
        """Check for required API keys based on model provider"""
        if model.startswith(('claude', 'haiku')):
            if not os.getenv("ANTHROPIC_API_KEY"):
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        elif model.startswith('gpt'):
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY not found in environment variables")

    def get_response(self, prompt: str) -> str:
        """Get move decision from language model"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            kwargs = {k: v for k, v in self.model_kwargs.items() 
                     if k in ['temperature', 'max_tokens']}
            
            response = completion(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise RuntimeError(f"Error getting LLM response: {str(e)}")

    def _create_system_prompt(self) -> str:
        personality_prompt = ""
        if self.personality:
            personality_prompt = f"\nYou are roleplaying with the following personality traits: {self.personality}\nMake your decisions and express your thoughts in alignment with this personality.\n"
        
        return f"""You are playing the Infinite Contract Game as {self.name}. 
Your goal is: {self.victory_condition}{personality_prompt}

Game Rules:
1. The game involves a shared Python code contract that both players modify
2. Variables x, y, and z start at 1 (not 0) and are modified through code execution
3. Each turn, you can play one card that adds a line of Python code
4. The entire contract executes from left to right each turn
5. You can see the current contract state, history, and available cards each turn
6. The game ends when either player achieves their victory condition

Key Points:
- Variables start at: x = 1, y = 1, z = 1
- The entire contract executes each turn
- Your code adds to the existing contract
- Think about the final values after full execution

Remember: Always format your response exactly as shown in the prompt, with a SCRATCH PAD section for your thinking and a SELECTED CARD number.
Express your personality in your SCRATCH PAD section."""

    def update_profile(self, game_result: Dict[str, Any]):
        storage_path = Path(os.getenv("STORAGE_PATH", "storage"))
        profiles_path = storage_path / "profiles.json"
        
        with open(profiles_path) as f:
            profiles = json.load(f)
        
        agent_id = self._generate_agent_id()
        profile = profiles[agent_id]
        
        # Update game stats
        profile["stats"]["total_games"] += 1
        
        if game_result["winner"] == self.name:
            profile["stats"]["games_won"] += 1
            profile["stats"]["win_rate"] = round(
                profile["stats"]["games_won"] / profile["stats"]["total_games"], 3
            )
            
            # Track victory condition
            victory_condition = game_result["victory_condition"]
            if victory_condition not in profile["stats"]["victory_conditions"]:
                profile["stats"]["victory_conditions"].append(victory_condition)
        
        # Update card type stats from turn history
        if "turn_history" in game_result:
            game_cards = {
                "aggressive": 0,
                "defensive": 0,
                "strategic": 0,
                "utility": 0
            }
            
            for turn in game_result["turn_history"]:
                if turn.get("player") == self.name and turn.get("success", False):
                    card_type = turn.get("card_type", "").lower()
                    if card_type in game_cards:
                        game_cards[card_type] += 1
                        profile["stats"]["card_type_stats"][card_type] += 1
            
            # Add per-game card usage
            profile["stats"]["card_type_stats"]["cards_per_game"].append(game_cards)
        
        # Create game history entry
        game_history_entry = {
            "timestamp": datetime.now().isoformat(),
            "total_turns": game_result["total_turns"],
            "winner": game_result["winner"],
            "victory_condition": game_result["victory_condition"],
            "card_usage": game_cards if "turn_history" in game_result else {}
        }
        
        # Append to game history
        if "game_history" not in profile:
            profile["game_history"] = []
        profile["game_history"].append(game_history_entry)
        
        # Save updated profiles
        with open(profiles_path, 'w') as f:
            json.dump(profiles, f, indent=4)

    def _generate_agent_id(self) -> str:
        """Generate a unique agent ID based on name, personality, model, and temperature"""
        personality_hash = hashlib.md5(str(self.personality).encode()).hexdigest()[:8]
        return f"{self.name}_{personality_hash}_{self.model}_{self.temperature}"