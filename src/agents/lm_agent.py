from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from litellm import completion
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from pathlib import Path

class LMAgent(BaseAgent):
    def __init__(self, 
                 name: str, 
                 model: str, 
                 victory_condition: str, 
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
        self.system_prompt = system_prompt or self._create_system_prompt()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model_kwargs = model_kwargs
        
        # Initialize profile if not in testing mode
        if not testing:
            self._initialize_profile()

    def _initialize_profile(self):
        """Initialize or load the agent's profile"""
        storage_path = Path(os.getenv("STORAGE_PATH", "storage"))
        profiles_path = storage_path / "profiles.json"
        
        # Create storage directory if it doesn't exist
        storage_path.mkdir(exist_ok=True)
        
        # Load or create profiles file
        if not profiles_path.exists():
            profiles = {}
        else:
            with open(profiles_path) as f:
                profiles = json.load(f)
        
        # Create agent profile if it doesn't exist
        agent_id = f"{self.name}_lmagent"
        if agent_id not in profiles:
            profiles[agent_id] = {
                "name": self.name,
                "model_type": "lmagent",
                "model_params": {
                    "model": self.model,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                },
                "stats": {
                    "total_games": 0,
                    "games_won": 0,
                    "avg_turns_to_win": 0,
                    "favorite_card_types": {},
                    "victory_conditions": {}
                },
                "game_history": []
            }
            
            # Save updated profiles
            with open(profiles_path, 'w') as f:
                json.dump(profiles, f, indent=4)

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
        return f"""You are playing the Infinite Contract Game as {self.name}. 
Your goal is: {self.victory_condition}

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

Remember: Always format your response exactly as shown in the prompt, with a SCRATCH PAD section for your thinking and a SELECTED CARD number."""

    def update_profile(self, game_result: Dict[str, Any]):
        """Update the agent's profile with game results"""
        storage_path = Path(os.getenv("STORAGE_PATH", "storage"))
        profiles_path = storage_path / "profiles.json"
        
        with open(profiles_path) as f:
            profiles = json.load(f)
        
        agent_id = f"{self.name}_lmagent"
        profile = profiles[agent_id]
        
        # Update stats
        profile["stats"]["total_games"] += 1
        if game_result.get("winner") == self.name:
            profile["stats"]["games_won"] += 1
        
        # Add game to history
        profile["game_history"].append({
            "winner": game_result.get("winner", "Draw"),
            "total_turns": game_result.get("total_turns", 0),
            "victory_condition": game_result.get("victory_condition", "Game ended in draw"),
            "timestamp": datetime.now().isoformat()
        })
        
        # Save updated profiles
        with open(profiles_path, 'w') as f:
            json.dump(profiles, f, indent=4)