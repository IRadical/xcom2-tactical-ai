from __future__ import annotations

from src.game.entities import Unit


class TacticalRenderer:
    def __init__(self, width: int = 10, height: int = 6):
        self.width = width
        self.height = height

    def _build_empty_grid(self) -> list[list[str]]:
        return [[" . " for _ in range(self.width)] for _ in range(self.height)]

    def _unit_token(self, unit: Unit) -> str:
        if unit.is_enemy:
            return f"E{unit.position[2]}"
        return f"S{unit.position[2]}"

    def render(
        self,
        soldiers: list[Unit],
        enemies: list[Unit],
        turn_number: int,
        action_log: list[str] | None = None,
    ) -> str:
        grid = self._build_empty_grid()

        all_units = [unit for unit in soldiers + enemies if unit.is_alive()]

        for unit in all_units:
            x, y, _z = unit.position
            if 0 <= x < self.width and 0 <= y < self.height:
                token = self._unit_token(unit)
                grid[y][x] = f"{token:>3}"

        lines: list[str] = []
        lines.append(f"\nTURN {turn_number}")
        lines.append("-" * 40)
        lines.append("Map legend: S=z-level soldier, E=z-level enemy")
        lines.append("")

        for y in range(self.height):
            row = "".join(grid[y])
            lines.append(f"{y:02d} {row}")

        x_axis = "   " + "".join(f"{x:>3}" for x in range(self.width))
        lines.append("")
        lines.append(x_axis)
        lines.append("")
        lines.append("UNITS")

        for unit in soldiers + enemies:
            status = "ALIVE" if unit.is_alive() else "DEAD "
            lines.append(
                f"- {unit.name:<10} "
                f"pos={unit.position} hp={unit.hp}/{unit.max_hp} "
                f"ammo={unit.ammo} cover={unit.cover} ap={unit.action_points} "
                f"status={status}"
            )

        if action_log:
            lines.append("")
            lines.append("ACTIONS")
            for entry in action_log:
                lines.append(f"- {entry}")

        return "\n".join(lines)