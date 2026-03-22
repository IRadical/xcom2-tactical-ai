from __future__ import annotations

from typing import Any

from src.game.entities import Unit
from src.game.game_state import GameState


def infer_role(unit_name: str, is_enemy: bool) -> str:
    if is_enemy:
        return "enemy"

    return "assault"


def infer_max_hp(unit_data: dict[str, Any]) -> int:
    hp = int(unit_data.get("HP", 1))
    return hp if hp > 0 else 1


def unit_from_export(unit_data: dict[str, Any]) -> Unit:
    is_enemy = unit_data.get("TeamName") == "ENEMY"

    name = str(unit_data.get("Name", "Unknown"))
    hp = int(unit_data.get("HP", 1))
    aim = int(unit_data.get("Aim", 0))
    ammo = int(unit_data.get("Ammo", 0))
    action_points = int(unit_data.get("AP", 0))

    x = int(unit_data.get("X", 0))
    y = int(unit_data.get("Y", 0))
    z = int(unit_data.get("Z", 0))
    position = (x, y, z)

    return Unit(
        name=name,
        hp=hp,
        aim=aim,
        ammo=ammo,
        position=position,
        is_enemy=is_enemy,
        cover=0,
        role=infer_role(name, is_enemy),
        max_hp=infer_max_hp(unit_data),
        medkit_charges=0,
        grenade_charges=0,
        ability_cooldowns={},
        hunkered_down=False,
        action_points=action_points,
    )


def game_state_from_exported_battle_state(battle_state: dict[str, Any]) -> GameState:
    allies_data = battle_state.get("allies", [])
    enemies_data = battle_state.get("enemies", [])

    soldiers = [unit_from_export(unit) for unit in allies_data]
    enemies = [unit_from_export(unit) for unit in enemies_data]

    active_soldier = next((unit for unit in soldiers if unit.action_points > 0), None)

    return GameState(
        soldiers=soldiers,
        enemies=enemies,
        active_soldier=active_soldier,
    )