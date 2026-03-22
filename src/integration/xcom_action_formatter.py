from __future__ import annotations

from typing import Any


def format_chosen_action(action: Any, active_soldier_name: str | None) -> str:
    action_type = getattr(action, "action_type", "unknown")
    score = getattr(action, "score", 0)
    target_name = getattr(action, "target_name", None)
    destination = getattr(action, "destination", None)
    target_position = getattr(action, "target_position", None)

    parts = [
        "CHOSEN_ACTION",
        f"Type={action_type}",
        f"SourceName={active_soldier_name or 'None'}",
        f"Score={score}",
        f"TargetName={target_name if target_name is not None else 'None'}",
        f"Destination={destination if destination is not None else 'None'}",
        f"TargetPosition={target_position if target_position is not None else 'None'}",
    ]

    return "|".join(parts)