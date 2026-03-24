from pathlib import Path

from src.integration.xcom_decision_bridge import choose_action_from_latest_log


def main() -> None:
    log_path = Path.home() / "Documents" / "My Games" / "XCOM2 War of the Chosen" / "XComGame" / "Logs" / "Launch.log"
    print(choose_action_from_latest_log(log_path))


if __name__ == "__main__":
    main()