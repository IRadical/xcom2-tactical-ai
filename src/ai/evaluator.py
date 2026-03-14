from src.game.actions import Action
from src.game.game_state import GameState
from src.game.entities import Unit

class ActionEvaluator:
    
    def score_shot(self, soldier: Unit, enemy: Unit) -> float:
        kill_bonus = 100 if enemy.hp <=4 else 0
        aim_score = soldier.aim
        low_hp_bonus = max (0, 10 - enemy.hp) * 5

        return aim_score + kill_bonus + low_hp_bonus
    
    def score_reload(self, soldier: Unit) -> float:
        if soldier.ammo == 0:
            return 80
        if soldier.ammo == 1:
            return 25
        return 5
    
    
    def choose_best_action(self, game_state: GameState) -> Action:
        soldier = game_state.soldier
        enemies = game_state.living_enemies()

        possible_actions: list[Action] = []

        if not enemies:
            return Action(action_type="wait", score = 0)
        
        for enemy in enemies:
            
            shot_score = self.score_shot(soldier, enemy)

            possible_actions.append(
                Action(
                    action_type="shoot",
                    target_name=enemy.name,
                    score=shot_score
                )
            )
        
        reload_score = self.score_reload(soldier)

        possible_actions.append(
            Action(
                action_type="reload",
                score=reload_score
            )
        )
        
        if soldier.ammo <= 0:
            reload_actions = [
                action for action in possible_actions
                if action.action_type == "reaload"
            ]
            return max(reload_actions, key=lambda action: action.score)
        
        return max(possible_actions, key=lambda action: action.score)
        
        
