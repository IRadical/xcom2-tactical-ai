from math import dist
from pathlib import Path

from src.integration.xcom_log_bridge import load_latest_battle_state
from src.integration.xcom_state_adapter import game_state_from_exported_battle_state


def enemy_distance(active_pos: tuple[int, int, int], enemy_pos: tuple[int, int, int]) -> float:
    return dist(active_pos, enemy_pos)


def main() -> None:
    log_path = Path.home() / "Documents" / "My Games" / "XCOM2 War of the Chosen" / "XComGame" / "Logs" / "Launch.log"

    battle_state = load_latest_battle_state(log_path)
    game_state = game_state_from_exported_battle_state(battle_state)

    active = game_state.active_soldier
    move_tiles = getattr(game_state, "available_move_tiles", [])

    print("ACTIVE SOLDIER:")
    print(active.name if active else None)
    print()

    print("ACTIVE POSITION:")
    print(active.position if active else None)
    print()

    print("AVAILABLE MOVE TILES COUNT:")
    print(len(move_tiles))
    print()

    print("FIRST 10 MOVE TILES:")
    for tile in move_tiles[:10]:
        print(tile)

    print()
    print("ENEMY DISTANCES FROM ACTIVE:")
    if active:
        for enemy in game_state.enemies:
            d = enemy_distance(active.position, enemy.position)
            print(
                {
                    "enemy": enemy.name,
                    "enemy_pos": enemy.position,
                    "distance": round(d, 2),
                }
            )


if __name__ == "__main__":
    main()