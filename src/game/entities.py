from __future__ import annotations

from dataclasses import dataclass, field

from src.game.geometry import Position, manhattan_3d


@dataclass
class Unit:
    name: str
    hp: int
    aim: int
    ammo: int
    position: Position
    is_enemy: bool
    cover: int = 0
    role: str = "assault"
    max_hp: int = 10
    medkit_charges: int = 0
    grenade_charges: int = 0
    ability_cooldowns: dict[str, int] = field(default_factory=dict)
    hunkered_down: bool = False
    action_points: int = 2

    def is_alive(self) -> bool:
        return self.hp > 0

    def distance_to(self, other: "Unit") -> int:
        return manhattan_3d(self.position, other.position)

    def clone_at_position(self, position: Position, cover: int) -> "Unit":
        return Unit(
            name=self.name,
            hp=self.hp,
            aim=self.aim,
            ammo=self.ammo,
            position=position,
            is_enemy=self.is_enemy,
            cover=cover,
            role=self.role,
            max_hp=self.max_hp,
            medkit_charges=self.medkit_charges,
            grenade_charges=self.grenade_charges,
            ability_cooldowns=dict(self.ability_cooldowns),
            hunkered_down=self.hunkered_down,
            action_points=self.action_points,
        )