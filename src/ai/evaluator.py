from src.game.actions import Action
from src.game.game_state import GameState
from src.game.entities import Unit


class ActionEvaluator:
    def is_flanked(self, attacker: Unit, target: Unit) -> bool:
        return attacker.distance_to(target) <= 2 and target.cover > 0

    def estimate_hit_chance(self, attacker: Unit, target: Unit) -> float:
        distance = attacker.distance_to(target)
        distance_penalty = distance * 5

        effective_cover = target.cover
        if self.is_flanked(attacker, target):
            effective_cover = 0

        raw_hit_chance = attacker.aim - distance_penalty - effective_cover
        return max(0, min(100, raw_hit_chance))

    def estimate_position_threat(
        self,
        soldier: Unit,
        enemies: list[Unit],
        position: tuple[int, int],
        cover: int,
    ) -> float:
        total_threat = 0.0

        for enemy in enemies:
            if not enemy.is_alive():
                continue

            distance = abs(position[0] - enemy.position[0]) + abs(position[1] - enemy.position[1])
            distance_penalty = distance * 5

            effective_cover = cover
            if distance <= 2 and cover > 0:
                effective_cover = 0

            estimated_enemy_hit = enemy.aim - distance_penalty - effective_cover
            estimated_enemy_hit = max(0, min(100, estimated_enemy_hit))

            total_threat += estimated_enemy_hit / 100.0

        return total_threat

    def score_shot(self, soldier: Unit, enemy: Unit, enemies: list[Unit]) -> float:
        hit_chance = self.estimate_hit_chance(soldier, enemy)

        kill_bonus = 180 if enemy.hp <= 4 else 0
        wounded_target_bonus = max(0, 12 - enemy.hp) * 8
        close_range_bonus = 15 if soldier.distance_to(enemy) <= 4 else 0
        flank_bonus = 50 if self.is_flanked(soldier, enemy) else 0

        low_accuracy_penalty = 0
        if hit_chance < 25:
            low_accuracy_penalty = 50
        elif hit_chance < 35:
            low_accuracy_penalty = 20

        current_position_threat = self.estimate_position_threat(
            soldier=soldier,
            enemies=enemies,
            position=soldier.position,
            cover=soldier.cover,
        )

        threat_penalty = 0.0
        if soldier.hp <= 4:
            threat_penalty = current_position_threat * 25
        elif soldier.hp <= 7:
            threat_penalty = current_position_threat * 12

        return (
            (hit_chance * 2.0)
            + kill_bonus
            + wounded_target_bonus
            + close_range_bonus
            + flank_bonus
            - low_accuracy_penalty
            - threat_penalty
        )

    def score_reload(self, soldier: Unit, best_hit_chance: float, enemies: list[Unit]) -> float:
        current_position_threat = self.estimate_position_threat(
            soldier=soldier,
            enemies=enemies,
            position=soldier.position,
            cover=soldier.cover,
        )

        if soldier.ammo == 0:
            return 100 - (current_position_threat * 10)

        if soldier.ammo == 1:
            if best_hit_chance < 15:
                return 8 - (current_position_threat * 8)
            return -35

        return -50

    def get_cover_value_for_position(self, destination: tuple[int, int]) -> int:
        x, y = destination

        if (x + y) % 5 == 0:
            return 40
        if (x + y) % 2 == 0:
            return 20
        return 0

    def score_move(
        self,
        soldier: Unit,
        enemies: list[Unit],
        destination: tuple[int, int],
        current_best_hit_chance: float,
    ) -> float:
        if not enemies:
            return 0

        distances = [
            abs(destination[0] - enemy.position[0]) + abs(destination[1] - enemy.position[1])
            for enemy in enemies
        ]
        closest_distance = min(distances)

        preferred_distance = 3
        distance_to_preferred = abs(closest_distance - preferred_distance)
        positioning_score = 28 - (distance_to_preferred * 5)

        cover_value = self.get_cover_value_for_position(destination)
        cover_bonus = cover_value * 0.9

        movement_cost = (
            abs(destination[0] - soldier.position[0])
            + abs(destination[1] - soldier.position[1])
        ) * 2

        survival_bonus = 0.0
        if soldier.hp <= 4:
            survival_bonus = cover_value * 1.5
        elif soldier.hp <= 7:
            survival_bonus = cover_value * 0.8

        shot_quality_bonus = 0.0
        if current_best_hit_chance < 20:
            shot_quality_bonus = 30
        elif current_best_hit_chance < 30:
            shot_quality_bonus = 15

        flank_setup_bonus = 0.0
        for enemy in enemies:
            future_distance = (
                abs(destination[0] - enemy.position[0])
                + abs(destination[1] - enemy.position[1])
            )
            if future_distance <= 2 and enemy.cover > 0:
                flank_setup_bonus = max(flank_setup_bonus, 18)

        destination_threat = self.estimate_position_threat(
            soldier=soldier,
            enemies=enemies,
            position=destination,
            cover=cover_value,
        )

        current_threat = self.estimate_position_threat(
            soldier=soldier,
            enemies=enemies,
            position=soldier.position,
            cover=soldier.cover,
        )

        threat_reduction_bonus = max(0.0, current_threat - destination_threat) * 40
        threat_penalty = destination_threat * 20

        if soldier.hp <= 4:
            threat_reduction_bonus *= 1.4
            threat_penalty *= 1.5

        return (
            positioning_score
            + cover_bonus
            + survival_bonus
            + shot_quality_bonus
            + flank_setup_bonus
            + threat_reduction_bonus
            - threat_penalty
            - movement_cost
        )

    def generate_move_actions(
        self,
        soldier: Unit,
        enemies: list[Unit],
        current_best_hit_chance: float,
    ) -> list[Action]:
        x, y = soldier.position

        possible_destinations = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
            (x + 1, y + 1),
            (x - 1, y - 1),
        ]

        actions: list[Action] = []

        for destination in possible_destinations:
            move_score = self.score_move(
                soldier,
                enemies,
                destination,
                current_best_hit_chance,
            )
            actions.append(
                Action(
                    action_type="move",
                    destination=destination,
                    score=move_score,
                )
            )

        return actions

    def choose_best_action(self, game_state: GameState) -> Action:
        soldier = game_state.soldier
        enemies = game_state.living_enemies()

        if not enemies:
            return Action(action_type="wait", score=0)

        shot_actions: list[Action] = []

        for enemy in enemies:
            if soldier.ammo > 0:
                shot_score = self.score_shot(soldier, enemy, enemies)
                shot_actions.append(
                    Action(
                        action_type="shoot",
                        target_name=enemy.name,
                        score=shot_score,
                    )
                )

        best_hit_chance = max(
            self.estimate_hit_chance(soldier, enemy)
            for enemy in enemies
        )

        if soldier.ammo > 0 and shot_actions and best_hit_chance >= 55:
            return max(shot_actions, key=lambda action: action.score)

        if soldier.ammo == 0:
            return Action(action_type="reload", score=100)

        possible_actions: list[Action] = []
        possible_actions.extend(shot_actions)

        possible_actions.append(
            Action(
                action_type="reload",
                score=self.score_reload(soldier, best_hit_chance, enemies),
            )
        )

        possible_actions.extend(
            self.generate_move_actions(soldier, enemies, best_hit_chance)
        )

        return max(possible_actions, key=lambda action: action.score)