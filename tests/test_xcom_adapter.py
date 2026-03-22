from pathlib import Path

from src.integration.xcom_log_bridge import load_latest_battle_state
from src.integration.xcom_state_adapter import game_state_from_exported_battle_state


def main() -> None:
    log_path = Path.home() / "Documents" / "My Games" / "XCOM2 WarOfTheChosen" / "XComGame" / "Logs" / "Launch.log"

    # Fallback por si tu carpeta tiene el nombre con espacios como antes
    if not log_path.exists():
        log_path = Path.home() / "Documents" / "My Games" / "XCOM2 War of the Chosen" / "XComGame" / "Logs" / "Launch.log"

    battle_state = load_latest_battle_state(log_path)
    game_state = game_state_from_exported_battle_state(battle_state)

    print("SOLDIERS:")
    for soldier in game_state.soldiers:
        print(
            soldier.name,
            soldier.hp,
            soldier.aim,
            soldier.ammo,
            soldier.position,
            soldier.action_points,
            soldier.is_enemy,
        )

    print()
    print("ENEMIES:")
    for enemy in game_state.enemies:
        print(
            enemy.name,
            enemy.hp,
            enemy.aim,
            enemy.ammo,
            enemy.position,
            enemy.action_points,
            enemy.is_enemy,
        )

    print()
    print("ACTIVE SOLDIER:")
    print(game_state.active_soldier.name if game_state.active_soldier else None)


if __name__ == "__main__":
    main()