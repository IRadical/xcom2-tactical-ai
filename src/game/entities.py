from dataclasses import dataclass

@dataclass
class Unit:
    name: str
    hp: int
    aim: int
    ammo: int
    position: int
    is_enemy: bool

    def is_alive(self) -> bool:
        return self.hp > 0