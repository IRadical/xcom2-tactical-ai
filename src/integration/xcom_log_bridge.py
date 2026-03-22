from __future__ import annotations

from pathlib import Path
from typing import Any


def parse_value(value: str) -> Any:
    value = value.strip()

    if value == "":
        return ""

    if "/" in value:
        left, right = value.split("/", 1)
        try:
            return {
                "current": float(left.strip()),
                "max": float(right.strip()),
            }
        except ValueError:
            return value

    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def parse_export_payload(payload: str) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for part in payload.split("|"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        result[key] = parse_value(value)

    return result


def normalize_unit(unit: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(unit)

    hp_value = normalized.get("HP")
    if isinstance(hp_value, dict):
        normalized["HP"] = hp_value["current"]
        normalized["MaxHP"] = hp_value["max"]

    return normalized


def parse_battle_state_from_log(log_path: str | Path) -> dict[str, Any]:
    log_path = Path(log_path)

    if not log_path.exists():
        raise FileNotFoundError(f"No existe el log: {log_path}")

    units: list[dict[str, Any]] = []
    move_tiles: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}
    active_unit_id: int | None = None

    with log_path.open("r", encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            line = raw_line.strip()

            if "EXPORT_UNIT|" in line:
                payload = line.split("EXPORT_UNIT|", 1)[1]
                unit_data = parse_export_payload(payload)
                units.append(normalize_unit(unit_data))

            elif "EXPORT_ACTIVE_MOVES_BEGIN|" in line:
                payload = line.split("EXPORT_ACTIVE_MOVES_BEGIN|", 1)[1]
                active_info = parse_export_payload(payload)
                if "UnitID" in active_info:
                    active_unit_id = int(active_info["UnitID"])

            elif "ACTIVE_MOVE_TILE|" in line:
                payload = line.split("ACTIVE_MOVE_TILE|", 1)[1]
                move_tiles.append(parse_export_payload(payload))

            elif "EXPORT_SUMMARY|" in line:
                payload = line.split("EXPORT_SUMMARY|", 1)[1]
                summary = parse_export_payload(payload)

    return {
        "units": units,
        "move_tiles": move_tiles,
        "summary": summary,
        "active_unit_id": active_unit_id,
    }


def split_units_by_team(units: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    allies = [u for u in units if u.get("Team") == "XCOM"]
    enemies = [u for u in units if u.get("Team") == "ENEMY"]
    others = [u for u in units if u.get("Team") not in {"XCOM", "ENEMY"}]

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
        "move_tiles": parsed["move_tiles"],
        "active_unit_id": parsed["active_unit_id"],
        "allies": grouped["allies"],
        "enemies": grouped["enemies"],
        "others": grouped["others"],
    }