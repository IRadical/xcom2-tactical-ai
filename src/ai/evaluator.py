from src.game.actions import Action
from src.game.game_state import GameState

class ActionEvaluator:
    def choose_best_action(self, game_state: GameState) -> Action:
        soldier = game_state.soldier
        enemies = game_state.living_enemies()

        if not enemies:
            return Action(action_type="wait")
        
        if soldier.ammo <= 0:
            return Action(action_type="reaload")
        
        target = min(enemies, key=lambda enemy: enemy.hp)

        return Action(
            action_type="shoot",
            target_name=target.name
        )
        
