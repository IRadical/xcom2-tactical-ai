from src.game.actions import Action
from src.game.game_state import GameState
from src.game.entities import Unit


class ActionEvaluator:
    def estimate_hit_chance(self, attacker: Unit, target: Unit) -> float:
        distance = attacker.distance_to(target)
        distance_penalty = distance * 5
        raw_hit_chance = attacker.aim - distance_penalty - target.cover
        return max(0, min(100, raw_hit_chance))

    def score_shot(self, soldier: Unit, enemy: Unit) -> float:
        hit_chance = self.estimate_hit_chance(soldier, enemy)

        kill_bonus = 140 if enemy.hp <= 4 else 0
        low_hp_bonus = max(0, 10 - enemy.hp) * 7
        close_range_bonus = 20 if soldier.distance_to(enemy) <= 4 else 0

        return (hit_chance * 2.2) + kill_bonus + low_hp_bonus + close_range_bonus

    def score_reload(self, soldier: Unit, enemies: list[Unit]) -> float:
        if soldier.ammo == 0:
            return 70

        if soldier.ammo == 1:
            if not enemies:
                return 15

            best_hit_chance = max(
                self.estimate_hit_chance(soldier, enemy)
                for enemy in enemies
            )

            if best_hit_chance < 25:
                return 20

            return -20

        return -30

    def get_cover_value_for_position(self, destination: int) -> int:
        cover_map = {
            -2: 0,
            -1: 20,
            0: 0,
            1: 20,
            2: 40,
            3: 20,
            4: 40,
            5: 0,
            6: 20,
            7: 40,
            8: 20,
            9: 0,
            10: 40,
        }
        return cover_map.get(destination, 0)

    def score_move(self, soldier: Unit, enemies: list[Unit], destination: int) -> float:
        if not enemies:
            return 0

        distances = [abs(destination - enemy.position) for enemy in enemies]
        closest_distance = min(distances)

        preferred_distance = 3
        distance_to_preferred = abs(closest_distance - preferred_distance)

        positioning_score = 35 - (distance_to_preferred * 6)

        cover_value = self.get_cover_value_for_position(destination)
        cover_bonus = cover_value * 0.9

        movement_cost = abs(destination - soldier.position) * 2

        survival_bonus = 0
        if soldier.hp <= 4:
            survival_bonus = cover_value * 1.2

        return positioning_score + cover_bonus + survival_bonus - movement_cost

    def generate_move_actions(self, soldier: Unit, enemies: list[Unit]) -> list[Action]:
        possible_destinations = [
            soldier.position - 2,
            soldier.position - 1,
            soldier.position + 1,
            soldier.position + 2,
        ]

        actions: list[Action] = []

        for destination in possible_destinations:
            move_score = self.score_move(soldier, enemies, destination)
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

        possible_actions: list[Action] = []

        if not enemies:
            return Action(action_type="wait", score=0)

        for enemy in enemies:
            if soldier.ammo > 0:
                shot_score = self.score_shot(soldier, enemy)
                possible_actions.append(
                    Action(
                        action_type="shoot",
                        target_name=enemy.name,
                        score=shot_score,
                    )
                )

        possible_actions.append(
            Action(
                action_type="reload",
                score=self.score_reload(soldier, enemies),
            )
        )

        possible_actions.extend(self.generate_move_actions(soldier, enemies))

        return max(possible_actions, key=lambda action: action.score)