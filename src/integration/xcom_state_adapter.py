from __future__ import annotations

from typing import Any

from src.game.entities import Unit
from src.game.game_state import GameState


def infer_role(unit_name: str, is_enemy: bool) -> str:
    if is_enemy:
        return "enemy"

    lower_name = unit_name.lower()

    if "sniper" in lower_name:
        return "sniper"
    if "grenadier" in lower_name:
        return "grenadier"
    if "specialist" in lower_name:
        return "support"
    if "ranger" in lower_name:
        return "assault"

    return "assault"


def infer_cover(unit_data: dict[str, Any]) -> int:
    return int(unit_data.get("Cover", 0))


def infer_hunkered_down(unit_data: dict[str, Any]) -> bool:
    return bool(unit_data.get("HunkeredDown", False))


def infer_max_hp(unit_data: dict[str, Any]) -> int:
    if "MaxHP" in unit_data:
        return int(float(unit_data["MaxHP"]))

    hp = int(float(unit_data.get("HP", 1)))
    return hp if hp > 0 else 1


def infer_medkit_charges(unit_data: dict[str, Any], is_enemy: bool) -> int:
    if is_enemy:
        return 0
    return int(unit_data.get("MedkitCharges", 0))


def infer_grenade_charges(unit_data: dict[str, Any], is_enemy: bool) -> int:
    if is_enemy:
        return 0
    return int(unit_data.get("GrenadeCharges", 0))


def infer_action_points(unit_data: dict[str, Any], active_unit_id: int | None) -> int:
    unit_id = int(unit_data.get("ID", -1))
    if active_unit_id is not None and unit_id == active_unit_id:
        return 2
    return 0


def unit_from_export(unit_data: dict[str, Any], active_unit_id: int | None) -> Unit:
    team_name = str(unit_data.get("Team", "OTHER"))
    is_enemy = team_name == "ENEMY"

    name = str(unit_data.get("Name", "Unknown"))
    hp = int(float(unit_data.get("HP", 1)))
    aim = int(float(unit_data.get("Aim", 0)))
    ammo = int(unit_data.get("Ammo1", 0))
    action_points = infer_action_points(unit_data, active_unit_id)

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
        cover=infer_cover(unit_data),
        role=infer_role(name, is_enemy),
        max_hp=infer_max_hp(unit_data),
        medkit_charges=infer_medkit_charges(unit_data, is_enemy),
        grenade_charges=infer_grenade_charges(unit_data, is_enemy),
        ability_cooldowns={},
        hunkered_down=infer_hunkered_down(unit_data),
        action_points=action_points,
    )


def game_state_from_exported_battle_state(battle_state: dict[str, Any]) -> GameState:
    allies_data = battle_state.get("allies", [])
    enemies_data = battle_state.get("enemies", [])
    active_unit_id = battle_state.get("active_unit_id")

    soldiers = [unit_from_export(unit, active_unit_id) for unit in allies_data]
    enemies = [unit_from_export(unit, active_unit_id) for unit in enemies_data]

    active_soldier = next((unit for unit in soldiers if unit.action_points > 0), None)

    return GameState(
        soldiers=soldiers,
        enemies=enemies,
        active_soldier=active_soldier,
    )