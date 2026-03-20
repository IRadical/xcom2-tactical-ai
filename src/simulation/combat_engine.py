from src.game.game_state import GameState
from src.ai.evaluator import ActionEvaluator
import random


class CombatEngine:
    def __init__(self, game_state: GameState, verbose: bool = True):
        self.game_state = game_state
        self.evaluator = ActionEvaluator()
        self.verbose = verbose

        self.metrics = {
            "shots_fired": 0,
            "shots_hit": 0,
            "damage_dealt": 0,
            "damage_taken": 0,
            "kills": 0,
            "action_counts": {
                "shoot": 0,
                "reload": 0,
                "move": 0,
                "wait": 0,
            },
        }

    def resolve_shot(self, attacker, target) -> None:
        if not self.evaluator.has_line_of_sight(attacker, target):
            if self.verbose:
                print(f"{attacker.name} has no line of sight to {target.name}")
            return

        hit_chance = self.evaluator.estimate_hit_chance(attacker, target)
        hit_roll = random.randint(1, 100)

        if not attacker.is_enemy:
            self.metrics["shots_fired"] += 1

        if hit_roll <= hit_chance:
            damage = random.randint(2, 4)
            previous_hp = target.hp
            target.hp -= damage
            target.hp = max(0, target.hp)
            actual_damage = previous_hp - target.hp

            if attacker.is_enemy:
                self.metrics["damage_taken"] += actual_damage
            else:
                self.metrics["shots_hit"] += 1
                self.metrics["damage_dealt"] += actual_damage
                if not target.is_alive():
                    self.metrics["kills"] += 1

            if self.verbose:
                print(
                    f"{attacker.name} hits {target.name} for {actual_damage} damage "
                    f"(hp={target.hp}, target cover={target.cover}, hit chance={round(hit_chance, 2)})"
                )
        else:
            if self.verbose:
                print(
                    f"{attacker.name} missed {target.name} "
                    f"(target cover={target.cover}, hit chance={round(hit_chance, 2)})"
                )

    def player_turn(self) -> None:
        soldiers = self.game_state.living_soldiers()

        for soldier in soldiers:
            local_state = GameState([soldier], self.game_state.enemies)
            action = self.evaluator.choose_best_action(local_state)

            if action.action_type in self.metrics["action_counts"]:
                self.metrics["action_counts"][action.action_type] += 1

            if self.verbose:
                print(f"\n{soldier.name} decision: {action.action_type}")

            if action.action_type == "shoot":
                targets = [
                    enemy for enemy in self.game_state.enemies
                    if enemy.is_alive() and enemy.name == action.target_name
                ]

                if targets and soldier.ammo > 0:
                    soldier.ammo -= 1
                    self.resolve_shot(soldier, targets[0])

            elif action.action_type == "reload":
                soldier.ammo = 5
                if self.verbose:
                    print(f"{soldier.name} reloads weapon")

            elif action.action_type == "move":
                soldier.position = action.destination
                soldier.cover = self.evaluator.get_cover_value_for_position(action.destination)
                if self.verbose:
                    print(
                        f"{soldier.name} moves to {action.destination} "
                        f"and gains cover {soldier.cover}"
                    )

    def enemy_turn(self) -> None:
        soldiers = self.game_state.living_soldiers()

        for enemy in self.game_state.enemies:
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

            target = random.choice(visible_targets)

            if self.verbose:
                print(f"{enemy.name} attacks {target.name}")

            self.resolve_shot(enemy, target)

            if target.hp <= 0 and self.verbose:
                print(f"{target.name} has been eliminated")

    def run_turn(self) -> None:
        self.player_turn()
        self.enemy_turn()

    def battle_over(self) -> bool:
        return (
            len(self.game_state.living_soldiers()) == 0
            or len(self.game_state.living_enemies()) == 0
        )