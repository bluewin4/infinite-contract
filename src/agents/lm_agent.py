from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from litellm import completion
from dotenv import load_dotenv
import os

class LMAgent(BaseAgent):
    def __init__(self, 
                 name: str, 
                 model: str, 
                 victory_condition: str, 
                 system_prompt: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 500,
                 **model_kwargs):
        # Load environment variables at initialization
        load_dotenv()
        
        # Check if required API keys are available based on model
        self._check_api_keys(model)
            
        super().__init__(name)
        self.model = model
        self.victory_condition = victory_condition
        self.system_prompt = system_prompt or self._create_system_prompt()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model_kwargs = model_kwargs
        
    def _check_api_keys(self, model: str):
        """Check for required API keys based on model provider"""
        if model.startswith(('claude', 'haiku')):
            if not os.getenv("ANTHROPIC_API_KEY"):
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        elif model.startswith('gpt'):
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY not found in environment variables")
        # Add other provider checks as needed
        
    def get_response(self, prompt: str) -> str:
        """Get move decision from language model"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Remove any model-specific kwargs that might not be supported
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
            # Log the error and raise with more context
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