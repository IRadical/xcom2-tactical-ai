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
        
        return max(possible_actions, key=lambda action: action.score)
        
        
