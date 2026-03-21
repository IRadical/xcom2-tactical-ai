from src.game.game_state import GameState
from src.ai.evaluator import ActionEvaluator
import random


class CombatEngine:
    def __init__(self, game_state: GameState, verbose: bool = True):
        self.game_state = game_state
        self.evaluator = ActionEvaluator()
        self.verbose = verbose
        self.focus_target_name: str | None = None
        self.overwatch_queue: set[str] = set()

        self.metrics = {
            "shots_fired": 0,
            "shots_hit": 0,
            "damage_dealt": 0,
            "damage_taken": 0,
            "kills": 0,
            "grenades_used": 0,
            "action_counts": {
                "shoot": 0,
                "reload": 0,
                "move": 0,
                "wait": 0,
                "overwatch": 0,
                "heal": 0,
                "hunker": 0,
                "grenade": 0,
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

    def _resolve_grenade(self, thrower, target_position: tuple[int, int] | None) -> None:
        if target_position is None:
            return

        if thrower.grenade_charges <= 0:
            return

        blast_radius = 1
        grenade_damage = 3
        affected_enemies = [
            enemy
            for enemy in self.game_state.living_enemies()
            if (
                abs(enemy.position[0] - target_position[0])
                + abs(enemy.position[1] - target_position[1])
            ) <= blast_radius
        ]

        if not affected_enemies:
            return

        thrower.grenade_charges -= 1
        self.metrics["grenades_used"] += 1

        if self.verbose:
            print(f"{thrower.name} throws grenade at {target_position}")

        for enemy in affected_enemies:
            previous_hp = enemy.hp
            enemy.hp = max(0, enemy.hp - grenade_damage)
            actual_damage = previous_hp - enemy.hp

            if enemy.cover > 0:
                enemy.cover = max(0, enemy.cover - 20)

            self.metrics["damage_dealt"] += actual_damage
            if not enemy.is_alive():
                self.metrics["kills"] += 1

            if self.verbose:
                print(
                    f"Grenade hits {enemy.name} for {actual_damage} damage "
                    f"(hp={enemy.hp}, cover={enemy.cover})"
                )

    def _decrement_cooldowns(self, soldier) -> None:
        updated = {}
        for ability_name, turns in soldier.ability_cooldowns.items():
            remaining = max(0, turns - 1)
            if remaining > 0:
                updated[ability_name] = remaining
        soldier.ability_cooldowns = updated

    def _reset_hunker_if_needed(self, soldier) -> None:
        if soldier.hunkered_down:
            soldier.cover = max(0, soldier.cover - 20)
            soldier.hunkered_down = False

    def _choose_focus_target(self, soldiers, enemies):
        visible_enemies = [
            enemy for enemy in enemies
            if any(
                self.evaluator.has_line_of_sight(soldier, enemy)
                for soldier in soldiers
            )
        ]

        if not visible_enemies:
            return None

        def target_priority(enemy):
            avg_hit = 0.0
            visible_count = 0

            for soldier in soldiers:
                if self.evaluator.has_line_of_sight(soldier, enemy):
                    avg_hit += self.evaluator.estimate_hit_chance(soldier, enemy)
                    visible_count += 1

            if visible_count > 0:
                avg_hit /= visible_count

            low_hp_bonus = max(0, 10 - enemy.hp) * 10
            visibility_bonus = visible_count * 20

            return avg_hit + low_hp_bonus + visibility_bonus

        best_enemy = max(visible_enemies, key=target_priority)
        return best_enemy.name

    def _choose_action_for_soldier(self, soldier):
        local_state = GameState(
            soldiers=self.game_state.living_soldiers(),
            enemies=self.game_state.enemies,
            active_soldier=soldier,
        )
        action = self.evaluator.choose_best_action(local_state)

        if action.action_type != "shoot" or not self.focus_target_name:
            return action

        focus_targets = [
            enemy for enemy in self.game_state.enemies
            if enemy.is_alive()
            and enemy.name == self.focus_target_name
            and self.evaluator.has_line_of_sight(soldier, enemy)
        ]

        if not focus_targets:
            return action

        focus_enemy = focus_targets[0]
        focus_score = self.evaluator.score_shot(
            soldier,
            focus_enemy,
            self.game_state.living_enemies(),
        )

        if focus_score >= action.score - 15:
            action.target_name = focus_enemy.name
            action.score = focus_score

        return action

    def _resolve_overwatch_for_enemy(self, enemy) -> None:
        if not enemy.is_alive():
            return

        active_names = list(self.overwatch_queue)

        for soldier_name in active_names:
            soldiers = [
                s for s in self.game_state.living_soldiers()
                if s.name == soldier_name and s.ammo > 0
            ]

            if not soldiers:
                self.overwatch_queue.discard(soldier_name)
                continue

            soldier = soldiers[0]

            if not self.evaluator.has_line_of_sight(soldier, enemy):
                continue

            soldier.ammo -= 1

            if self.verbose:
                print(f"{soldier.name} triggers overwatch on {enemy.name}")

            self.resolve_shot(soldier, enemy)
            self.overwatch_queue.discard(soldier_name)

            if not enemy.is_alive():
                break

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
        heal_amount = 4

        previous_hp = target.hp
        target.hp = min(target.max_hp, target.hp + heal_amount)
        actual_heal = target.hp - previous_hp
        healer.medkit_charges -= 1
        healer.ability_cooldowns["heal"] = 2

        if self.verbose:
            print(f"{healer.name} heals {target.name} for {actual_heal} HP")

    def player_turn(self) -> None:
        soldiers = self.game_state.living_soldiers()
        enemies = self.game_state.living_enemies()
        self.overwatch_queue = set()

        for soldier in soldiers:
            self._decrement_cooldowns(soldier)
            self._reset_hunker_if_needed(soldier)

        self.focus_target_name = self._choose_focus_target(soldiers, enemies)

        if self.verbose and self.focus_target_name:
            print(f"\nSquad focus target: {self.focus_target_name}")

        for soldier in soldiers:
            action = self._choose_action_for_soldier(soldier)

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

            elif action.action_type == "overwatch":
                if soldier.ammo > 0:
                    self.overwatch_queue.add(soldier.name)
                    if self.verbose:
                        print(f"{soldier.name} enters overwatch")

            elif action.action_type == "heal":
                self._resolve_heal(soldier, action.target_name)

            elif action.action_type == "hunker":
                if not soldier.hunkered_down:
                    soldier.cover = min(60, soldier.cover + 20)
                    soldier.hunkered_down = True
                    if self.verbose:
                        print(f"{soldier.name} hunkers down and increases cover to {soldier.cover}")

            elif action.action_type == "grenade":
                self._resolve_grenade(soldier, action.target_position)

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