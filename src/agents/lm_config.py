from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class LMConfig:
    model: str
    temperature: float = 0.7
    max_tokens: int = 500
    system_prompt: Optional[str] = None
    extra_params: Dict[str, Any] = None 