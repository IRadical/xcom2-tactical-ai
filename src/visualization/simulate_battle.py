from __future__ import annotations

import random

from src.ai.evaluator import ActionEvaluator
from src.game.entities import Unit
from src.game.game_state import GameState
from src.simulation.combat_engine import CombatEngine
from src.visualization.tactical_render import TacticalRenderer


class VisualCombatEngine(CombatEngine):
    def __init__(self, game_state: GameState, verbose: bool = False):
        super().__init__(game_state=game_state, verbose=verbose)
        self.turn_action_log: list[str] = []

    def _log(self, message: str) -> None:
        self.turn_action_log.append(message)

    def resolve_shot(self, attacker, target) -> None:
        if not self.evaluator.has_line_of_sight(attacker, target):
            self._log(f"{attacker.name} has no line of sight to {target.name}")
            return

        hit_chance = self.evaluator.estimate_hit_chance(attacker, target)
        hit_roll = random.randint(1, 100)

        if not attacker.is_enemy:
            self.metrics["shots_fired"] += 1

        if hit_roll <= hit_chance:
            damage = random.randint(2, 4)
            previous_hp = target.hp
            target.hp = max(0, target.hp - damage)
            actual_damage = previous_hp - target.hp

            if attacker.is_enemy:
                self.metrics["damage_taken"] += actual_damage
            else:
                self.metrics["shots_hit"] += 1
                self.metrics["damage_dealt"] += actual_damage
                if not target.is_alive():
                    self.metrics["kills"] += 1

            self._log(
                f"{attacker.name} hits {target.name} for {actual_damage} "
                f"(hp={target.hp}, hit={round(hit_chance, 1)}%)"
            )
        else:
            self._log(
                f"{attacker.name} misses {target.name} "
                f"(hit={round(hit_chance, 1)}%)"
            )

    def _resolve_grenade(self, thrower, target_position) -> None:
        if target_position is None or thrower.grenade_charges <= 0:
            return

        grenade_damage = 3
        affected_enemies = [
            enemy
            for enemy in self.game_state.living_enemies()
            if enemy.position[2] == target_position[2]
            and abs(enemy.position[0] - target_position[0])
            + abs(enemy.position[1] - target_position[1]) <= 1
        ]

        if not affected_enemies:
            return

        thrower.grenade_charges -= 1
        self.metrics["grenades_used"] += 1
        self._log(f"{thrower.name} throws grenade at {target_position}")

        for enemy in affected_enemies:
            previous_hp = enemy.hp
            enemy.hp = max(0, enemy.hp - grenade_damage)
            actual_damage = previous_hp - enemy.hp

            if enemy.position == target_position and enemy.cover > 0:
                enemy.cover = max(0, enemy.cover - 20)

            self.metrics["damage_dealt"] += actual_damage
            if not enemy.is_alive():
                self.metrics["kills"] += 1

            self._log(
                f"Grenade hits {enemy.name} for {actual_damage} "
                f"(hp={enemy.hp}, cover={enemy.cover})"
            )

    def _resolve_heal(self, healer, target_name: str | None) -> None:
        if target_name is None:
            return
        if healer.medkit_charges <= 0:
            return
        if healer.ability_cooldowns.get("heal", 0) > 0:
            return

        valid_targets = [
            ally for ally in self.game_state.living_soldiers()
            if ally.name == target_name and healer.distance_to(ally) <= 2
        ]

        if not valid_targets:
            return

        target = valid_targets[0]
        previous_hp = target.hp
        target.hp = min(target.max_hp, target.hp + 4)
        actual_heal = target.hp - previous_hp
        healer.medkit_charges -= 1
        healer.ability_cooldowns["heal"] = 2

        self._log(f"{healer.name} heals {target.name} for {actual_heal}")

    def _run_single_soldier_turn(self, soldier) -> None:
        while soldier.is_alive() and soldier.action_points > 0 and self.game_state.living_enemies():
            action = self._choose_action_for_soldier(soldier)

            if action.action_type in self.metrics["action_counts"]:
                self.metrics["action_counts"][action.action_type] += 1

            self._log(f"{soldier.name} chooses {action.action_type} (ap={soldier.action_points})")

            if action.action_type == "shoot":
                targets = [
                    enemy for enemy in self.game_state.enemies
                    if enemy.is_alive() and enemy.name == action.target_name
                ]
                if targets and soldier.ammo > 0:
                    soldier.ammo -= 1
                    self.resolve_shot(soldier, targets[0])
                self._consume_action_points(soldier, "shoot")

            elif action.action_type == "reload":
                soldier.ammo = 5
                self._log(f"{soldier.name} reloads")
                self._consume_action_points(soldier, "reload")

            elif action.action_type == "move":
                if action.destination is not None:
                    soldier.position = action.destination
                    soldier.cover = self.evaluator.get_cover_value_for_position(action.destination)
                    self._log(
                        f"{soldier.name} moves to {action.destination} "
                        f"(cover={soldier.cover})"
                    )
                self._consume_action_points(soldier, "move")

            elif action.action_type == "overwatch":
                if soldier.ammo > 0:
                    self.overwatch_queue.add(soldier.name)
                    self._log(f"{soldier.name} enters overwatch")
                self._consume_action_points(soldier, "overwatch")

            elif action.action_type == "heal":
                self._resolve_heal(soldier, action.target_name)
                self._consume_action_points(soldier, "heal")

            elif action.action_type == "hunker":
                if not soldier.hunkered_down:
                    soldier.cover = min(60, soldier.cover + 20)
                    soldier.hunkered_down = True
                    self._log(f"{soldier.name} hunkers down (cover={soldier.cover})")
                self._consume_action_points(soldier, "hunker")

            elif action.action_type == "grenade":
                self._resolve_grenade(soldier, action.target_position)
                self._consume_action_points(soldier, "grenade")

            else:
                self._consume_action_points(soldier, "wait")

    def enemy_turn(self) -> None:
        for enemy in self.game_state.enemies:
            if not enemy.is_alive():
                continue

            self._resolve_overwatch_for_enemy(enemy)

            if not enemy.is_alive():
                continue

            soldiers = self.game_state.living_soldiers()
            if not soldiers:
                return

            visible_targets = [
                soldier for soldier in soldiers
                if self.evaluator.has_line_of_sight(enemy, soldier)
            ]

            if not visible_targets:
                continue

            target = min(visible_targets, key=lambda soldier: soldier.hp)
            self._log(f"{enemy.name} attacks {target.name}")
            self.resolve_shot(enemy, target)


def build_demo_battle() -> GameState:
    soldiers = [
        Unit(
            name="Assault-1",
            hp=10,
            aim=75,
            ammo=5,
            position=(0, 0, 0),
            is_enemy=False,
            cover=20,
            role="assault",
            max_hp=10,
            grenade_charges=1,
        ),
        Unit(
            name="Sniper-1",
            hp=9,
            aim=80,
            ammo=5,
            position=(1, 0, 1),
            is_enemy=False,
            cover=20,
            role="sniper",
            max_hp=9,
        ),
        Unit(
            name="Support-1",
            hp=10,
            aim=68,
            ammo=5,
            position=(0, 1, 0),
            is_enemy=False,
            cover=20,
            role="support",
            max_hp=10,
            medkit_charges=2,
            grenade_charges=1,
        ),
    ]

    enemies = [
        Unit(
            name="Sectoid",
            hp=5,
            aim=65,
            ammo=2,
            position=(5, 1, 0),
            is_enemy=True,
            cover=20,
            role="assault",
            max_hp=6,
        ),
        Unit(
            name="Trooper",
            hp=6,
            aim=60,
            ammo=3,
            position=(6, 2, 1),
            is_enemy=True,
            cover=20,
            role="assault",
            max_hp=7,
        ),
        Unit(
            name="StunLancer",
            hp=7,
            aim=62,
            ammo=3,
            position=(7, 1, 0),
            is_enemy=True,
            cover=0,
            role="assault",
            max_hp=7,
        ),
    ]

    return GameState(soldiers=soldiers, enemies=enemies)


def main() -> None:
    random.seed(42)

    game_state = build_demo_battle()
    engine = VisualCombatEngine(game_state=game_state, verbose=False)
    renderer = TacticalRenderer(width=10, height=6)

    turn = 0
    max_turns = 8

    while not engine.battle_over() and turn < max_turns:
        turn += 1
        engine.turn_action_log = []
        engine.run_turn()

        output = renderer.render(
            soldiers=game_state.soldiers,
            enemies=game_state.enemies,
            turn_number=turn,
            action_log=engine.turn_action_log,
        )
        print(output)
        print("\n" + "=" * 60 + "\n")

    print("FINAL RESULT")
    print("-" * 40)
    print("Soldiers alive:", len(game_state.living_soldiers()))
    print("Enemies alive:", len(game_state.living_enemies()))
    print("Metrics:", engine.metrics)


if __name__ == "__main__":
    main()