from __future__ import annotations

from dataclasses import dataclass

from src.game.geometry import Position


@dataclass
class Action:
    action_type: str
    score: float
    target_name: str | None = None
    destination: Position | None = None
    target_position: Position | None = None