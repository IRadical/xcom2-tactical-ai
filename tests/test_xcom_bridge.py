from pathlib import Path

from src.integration.xcom_log_bridge import load_latest_battle_state


def main() -> None:
    log_path = Path.home() / "Documents" / "My Games" / "XCOM2 War of the Chosen" / "XComGame" / "Logs" / "Launch.log"

    battle_state = load_latest_battle_state(log_path)

    print("SUMMARY:")
    print(battle_state["summary"])
    print()

    print("ALLIES:")
    for unit in battle_state["allies"]:
        print(unit)

    print()
    print("ENEMIES:")
    for unit in battle_state["enemies"]:
        print(unit)

    print()
    print("OTHERS:")
    for unit in battle_state["others"]:
        print(unit)


if __name__ == "__main__":
    main()