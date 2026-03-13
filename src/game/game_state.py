from dataclasses import dataclass
from src.game.entities import Unit

@dataclass
class GameState:
    soldier: Unit
    enemies: list[Unit]

    def living_enemies(self) -> list [Unit]:
        return [enemy for enemy in self.enemies if enemy.is_alive()]