from __future__ import annotations

from math import dist
from pathlib import Path
from typing import Any

from src.ai.evaluator import ActionEvaluator
from src.integration.xcom_action_formatter import format_chosen_action
from src.integration.xcom_log_bridge import load_latest_battle_state
from src.integration.xcom_state_adapter import game_state_from_exported_battle_state


def distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return dist(a, b)


def choose_nearest_enemy(active_unit: Any, enemies: list[Any]) -> Any | None:
    if not enemies:
        return None
    return min(enemies, key=lambda enemy: distance(active_unit.position, enemy.position))


def choose_best_move_tile_toward_enemy(
    active_unit: Any,
    enemy: Any,
    move_tiles: list[dict[str, Any]],
) -> tuple[int, int, int] | None:
    if not move_tiles:
        return None

    best_tile: tuple[int, int, int] | None = None
    best_distance = float("inf")

    for tile in move_tiles:
        tile_pos = (int(tile["TileX"]), int(tile["TileY"]), int(tile["TileZ"]))
        d = distance(tile_pos, enemy.position)

        if d < best_distance:
            best_distance = d
            best_tile = tile_pos

    return best_tile


def format_move_action(source_name: str, target_name: str, destination: tuple[int, int, int]) -> str:
    return (
        "CHOSEN_ACTION"
        f"|Type=move"
        f"|SourceName={source_name}"
        f"|TargetName={target_name}"
        f"|Destination={destination}"
    )


def choose_action_from_latest_log(log_path: str | Path) -> str:
    battle_state = load_latest_battle_state(log_path)
    game_state = game_state_from_exported_battle_state(battle_state)

    active = game_state.active_soldier
    if active is None:
        return "CHOSEN_ACTION|Type=wait|SourceName=None|TargetName=None|Destination=None"

    evaluator = ActionEvaluator()
    ai_action = evaluator.choose_best_action(game_state)

    # Si la IA produce algo ofensivo útil, expórtalo tal cual
    if getattr(ai_action, "action_type", None) in {"shoot", "grenade", "overwatch", "reload", "heal"}:
        return format_chosen_action(ai_action, active.name)

    # Fallback: movimiento legal hacia enemigo más cercano
    move_tiles = battle_state.get("move_tiles", [])
    nearest_enemy = choose_nearest_enemy(active, game_state.enemies)

    if nearest_enemy is None:
        return "CHOSEN_ACTION|Type=wait|SourceName=None|TargetName=None|Destination=None"

    best_tile = choose_best_move_tile_toward_enemy(active, nearest_enemy, move_tiles)
    if best_tile is None:
        return "CHOSEN_ACTION|Type=wait|SourceName=None|TargetName=None|Destination=None"

    return format_move_action(active.name, nearest_enemy.name, best_tile)


def main() -> None:
    log_path = Path.home() / "Documents" / "My Games" / "XCOM2 War of the Chosen" / "XComGame" / "Logs" / "Launch.log"
    print(choose_action_from_latest_log(log_path))


if __name__ == "__main__":
    main()