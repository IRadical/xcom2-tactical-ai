from math import dist
from pathlib import Path

from src.integration.xcom_log_bridge import load_latest_battle_state
from src.integration.xcom_state_adapter import game_state_from_exported_battle_state


def distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return dist(a, b)


def choose_nearest_enemy(active_unit, enemies):
    return min(enemies, key=lambda enemy: distance(active_unit.position, enemy.position))


def choose_best_move_tile_toward_enemy(active_unit, enemy, move_tiles):
    if not move_tiles:
        return None

    best_tile = None
    best_distance = float("inf")

    for tile in move_tiles:
        tile_pos = (int(tile["TileX"]), int(tile["TileY"]), int(tile["TileZ"]))
        d = distance(tile_pos, enemy.position)

        if d < best_distance:
            best_distance = d
            best_tile = tile_pos

    return best_tile, best_distance


def main() -> None:
    log_path = Path.home() / "Documents" / "My Games" / "XCOM2 War of the Chosen" / "XComGame" / "Logs" / "Launch.log"

    battle_state = load_latest_battle_state(log_path)
    game_state = game_state_from_exported_battle_state(battle_state)

    active = game_state.active_soldier
    move_tiles = getattr(game_state, "available_move_tiles", [])
    enemies = game_state.enemies

    print("ACTIVE SOLDIER:")
    print(active.name if active else None)
    print()

    if active is None:
        print("No active soldier found.")
        return

    if not enemies:
        print("No enemies found.")
        return

    nearest_enemy = choose_nearest_enemy(active, enemies)
    print("NEAREST ENEMY:")
    print(
        {
            "name": nearest_enemy.name,
            "position": nearest_enemy.position,
            "distance_from_active": round(distance(active.position, nearest_enemy.position), 2),
        }
    )
    print()

    result = choose_best_move_tile_toward_enemy(active, nearest_enemy, move_tiles)
    if result is None:
        print("No move tile found.")
        return

    best_tile, best_distance = result

    print("BEST MOVE TILE:")
    print(
        {
            "tile": best_tile,
            "distance_to_enemy_after_move": round(best_distance, 2),
        }
    )
    print()

    print("EXPORT:")
    print(
        "CHOSEN_ACTION"
        f"|Type=move"
        f"|SourceName={active.name}"
        f"|TargetName={nearest_enemy.name}"
        f"|Destination={best_tile}"
    )


if __name__ == "__main__":
    main()