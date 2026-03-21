from dataclasses import dataclass

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

    def is_alive(self) -> bool:
        return self.hp > 0
    
    def distance_to(self, other:"Unit") -> int:
        dx = abs(self.position[0] - other.position[0])
        dy = abs(self.position[1] - other.position[1])
        return dx + dy