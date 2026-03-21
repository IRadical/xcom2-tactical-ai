from dataclasses import dataclass, field

@dataclass
class Unit:
    name: str
    hp: int
    aim: int
    ammo: int
    position: tuple[int, int]
    is_enemy: bool
    cover: int = 0
    role: str = "assault"
    max_hp: int = 10
    medkit_charges: int = 0
    ability_cooldowns: dict[str, int] = field(default_factory = dict)
    hunkered_down: bool = False

    def is_alive(self) -> bool:
        return self.hp > 0
    
    def distance_to(self, other:"Unit") -> int:
        dx = abs(self.position[0] - other.position[0])
        dy = abs(self.position[1] - other.position[1])
        return dx + dy