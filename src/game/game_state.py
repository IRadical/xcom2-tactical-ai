from __future__ import annotations

from src.game.entities import Unit


class GameState:
    def __init__(
        self,
        soldiers: list[Unit],
        enemies: list[Unit],
        active_soldier: Unit | None = None,
    ):
        self.soldiers = soldiers
        self.enemies = enemies
        self.active_soldier = active_soldier

    @property
    def soldier(self) -> Unit:
        if self.active_soldier is not None:
            return self.active_soldier

        living = self.living_soldiers()
        if living:
            return living[0]
        return self.soldiers[0]

    def living_enemies(self) -> list[Unit]:
        return [enemy for enemy in self.enemies if enemy.is_alive()]

    def living_soldiers(self) -> list[Unit]:
        return [soldier for soldier in self.soldiers if soldier.is_alive()]