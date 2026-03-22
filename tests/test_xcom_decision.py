from pathlib import Path

from src.ai.evaluator import ActionEvaluator
from src.integration.xcom_action_formatter import format_chosen_action
from src.integration.xcom_log_bridge import load_latest_battle_state
from src.integration.xcom_state_adapter import game_state_from_exported_battle_state


def main() -> None:
    log_path = Path.home() / "Documents" / "My Games" / "XCOM2 War of the Chosen" / "XComGame" / "Logs" / "Launch.log"

    battle_state = load_latest_battle_state(log_path)
    game_state = game_state_from_exported_battle_state(battle_state)

    evaluator = ActionEvaluator()
    action = evaluator.choose_best_action(game_state)

    active_name = game_state.active_soldier.name if game_state.active_soldier else None

    print("ACTIVE SOLDIER:")
    print(active_name)
    print()

    print("CHOSEN ACTION OBJECT:")
    print(action)
    print()

    print("CHOSEN ACTION DETAILS:")
    for attr in ["action_type", "type", "target", "target_name", "destination", "target_position", "score"]:
        if hasattr(action, attr):
            print(f"{attr}: {getattr(action, attr)}")

    print()
    print("EXPORT:")
    print(format_chosen_action(action, active_name))


if __name__ == "__main__":
    main()