from src.game.actions import Action
from src.game.game_state import GameState
from src.game.entities import Unit

class ActionEvaluator:
    
    def estimate_hit_chance(self, soldier: Unit, enemy: Unit) -> float:
        distance = soldier.distance_to(enemy)
        distance_penalty = distance * 5
        raw_hit_chance = soldier.aim - distance_penalty

        return max(0, min(100, raw_hit_chance))
    
    def score_shot(self, soldier: Unit, enemy: Unit) -> float:
        hit_chance = self.estimate_hit_chance(soldier, enemy)
        kill_bonus = 100 if enemy.hp <=4 else 0
        low_hp_bonus = max (0, 10 - enemy.hp) * 5
        distance_bonus = max(0, 20 - soldier.distance_to(enemy) * 2)

        return hit_chance + kill_bonus + low_hp_bonus + distance_bonus
    
    def score_reload(self, soldier: Unit, enemies: list[Unit]) -> float:
        if soldier.ammo == 0:
            return 90
        
        if soldier.ammo == 1 and enemies:
            closest_enemy_distance = min(soldier.distance_to(enemy) for enemy in enemies)
            if closest_enemy_distance > 5:
                return 40
        return 5
    
    def score_move(self, new_position: int, soldier: Unit, enemies: list[Unit]) -> float:
        if not enemies:
            return 0
        
        projected_soldier = Unit(
            name=soldier.name,
            hp=soldier.hp,
            aim=soldier.aim,
            ammo=soldier.ammo,
            position=new_position,
            is_enemy=soldier.is_enemy
        )

        closest_distance = min(projected_soldier.distance_to(enemy) for enemy in enemies)
        
        ideal_distance = 3
        distance_score = max(0, 40 - abs(closest_distance - ideal_distance) * 10)

        forward_bonus = 10 if new_position > soldier.position else 0
        overexposure_penalty = -20 if closest_distance <= 1 else 0

        return distance_score + forward_bonus + overexposure_penalty
    
    def generate_movement_actions(self, soldier: Unit, enemies: list[Unit]) -> list[Action]:
        candidate_positions = [
            soldier.position - 2,
            soldier.position - 1,
            soldier.position,
            soldier.position + 1,
            soldier.position + 2
        ]

        actions: list[Action] = []

        for position in candidate_positions:
            score = self.score_move(position, soldier, enemies)
            actions.append(
                Action(
                    action_type="move",
                    destination=position,
                    score=score
                )
            )
        return actions

    def choose_best_action(self, game_state: GameState) -> Action:
        soldier = game_state.soldier
        enemies = game_state.living_enemies()

        possible_actions: list[Action] = []

        if not enemies:
            return Action(action_type="wait", score = 0)
        
        for enemy in enemies:
            if soldier.ammo > 0:
                shot_score = self.score_shot(soldier, enemy)
                possible_actions.append(
                    Action(
                        action_type="shoot",
                        target_name=enemy.name,
                        score=shot_score
                    )
                )
        
        reload_score = self.score_reload(soldier, enemies)

        possible_actions.append(
            Action(
                action_type="reload",
                score=reload_score
            )
        )

        movement_actions = self.generate_movement_actions(soldier, enemies)
        possible_actions.extend(movement_actions)
        
        return max(possible_actions, key=lambda action: action.score)
        
        
