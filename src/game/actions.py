from dataclasses import dataclass 

@dataclass
class Action:
    action_type: str
    score: float
    target_name: str | None = None
    destination: int | None = None 