from pathlib import Path

from src.integration.xcom_log_bridge import load_latest_battle_state
from src.integration.xcom_state_adapter import game_state_from_exported_battle_state


def print_unit(unit) -> None:
    print(
        {
            "name": unit.name,
            "hp": unit.hp,
            "max_hp": unit.max_hp,
            "aim": unit.aim,
            "ammo": unit.ammo,
            "position": unit.position,
            "action_points": unit.action_points,
            "is_enemy": unit.is_enemy,
            "cover": unit.cover,
            "role": unit.role,
            "medkit_charges": unit.medkit_charges,
            "grenade_charges": unit.grenade_charges,
            "hunkered_down": unit.hunkered_down,
            "ability_cooldowns": unit.ability_cooldowns,
        }
    )


def main() -> None:
    log_path = Path.home() / "Documents" / "My Games" / "XCOM2 War of the Chosen" / "XComGame" / "Logs" / "Launch.log"

    battle_state = load_latest_battle_state(log_path)
    game_state = game_state_from_exported_battle_state(battle_state)

    print("SUMMARY:")
    print(battle_state["summary"])
    print()

    print("MOVE TILES:")
    for tile in battle_state["move_tiles"][:10]:
        print(tile)

    print()
    print("SOLDIERS:")
    for soldier in game_state.soldiers:
        print_unit(soldier)

    print()
    print("ENEMIES:")
    for enemy in game_state.enemies:
        print_unit(enemy)

    print()
    print("ACTIVE SOLDIER:")
    print(game_state.active_soldier.name if game_state.active_soldier else None)


if __name__ == "__main__":
    main()