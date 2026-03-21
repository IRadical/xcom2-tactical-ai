from __future__ import annotations

from dataclasses import dataclass

Position = tuple[int, int, int]


@dataclass(frozen=True)
class Tile:
    x: int
    y: int
    z: int

    def to_position(self) -> Position:
        return (self.x, self.y, self.z)


def manhattan_3d(a: Position, b: Position, z_weight: int = 2) -> int:
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    dz = abs(a[2] - b[2])
    return dx + dy + (dz * z_weight)


def chebyshev_2d(a: Position, b: Position) -> int:
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy)


def same_level(a: Position, b: Position) -> bool:
    return a[2] == b[2]


def elevation_delta(a: Position, b: Position) -> int:
    return a[2] - b[2]


def within_grenade_radius(center: Position, target: Position, radius: int = 1) -> bool:
    same_floor = center[2] == target[2]
    if not same_floor:
        return False

    dx = abs(center[0] - target[0])
    dy = abs(center[1] - target[1])
    return dx + dy <= radius


def positions_adjacent(a: Position, b: Position) -> bool:
    if a == b:
        return False

    if abs(a[2] - b[2]) > 1:
        return False

    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    dz = abs(a[2] - b[2])

    if dz == 0:
        return dx <= 1 and dy <= 1

    return dx == 0 and dy == 0 and dz == 1


def generate_neighbor_positions(origin: Position) -> list[Position]:
    x, y, z = origin
    candidates = [
        (x + 1, y, z),
        (x - 1, y, z),
        (x, y + 1, z),
        (x, y - 1, z),
        (x + 1, y + 1, z),
        (x - 1, y - 1, z),
        (x + 1, y - 1, z),
        (x - 1, y + 1, z),
        (x, y, z + 1),
    ]

    if z > 0:
        candidates.append((x, y, z - 1))

    return candidates