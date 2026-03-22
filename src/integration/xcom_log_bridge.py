from __future__ import annotations

from pathlib import Path
from typing import Any


def parse_value(value: str) -> Any:
    value = value.strip()

    if value == "":
        return ""

    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def parse_export_payload(payload: str) -> dict[str, Any]:
    result: dict[str, Any] = {}

    parts = payload.split("|")
    for part in parts:
        if "=" not in part:
            continue

        key, value = part.split("=", 1)
        result[key] = parse_value(value)

    return result


def parse_battle_state_from_log(log_path: str | Path) -> dict[str, Any]:
    log_path = Path(log_path)

    if not log_path.exists():
        raise FileNotFoundError(f"No existe el log: {log_path}")

    units: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}

    with log_path.open("r", encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            line = raw_line.strip()

            if "EXPORT_UNIT|" in line:
                payload = line.split("EXPORT_UNIT|", 1)[1]
                units.append(parse_export_payload(payload))

            elif "EXPORT_SUMMARY|" in line:
                payload = line.split("EXPORT_SUMMARY|", 1)[1]
                summary = parse_export_payload(payload)

    return {
        "units": units,
        "summary": summary,
    }


def split_units_by_team(units: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    allies = [u for u in units if u.get("TeamName") == "XCOM"]
    enemies = [u for u in units if u.get("TeamName") == "ENEMY"]
    others = [u for u in units if u.get("TeamName") not in {"XCOM", "ENEMY"}]

    return {
        "allies": allies,
        "enemies": enemies,
        "others": others,
    }


def load_latest_battle_state(log_path: str | Path) -> dict[str, Any]:
    parsed = parse_battle_state_from_log(log_path)
    grouped = split_units_by_team(parsed["units"])

    return {
        "summary": parsed["summary"],
        "units": parsed["units"],
        "allies": grouped["allies"],
        "enemies": grouped["enemies"],
        "others": grouped["others"],
    }