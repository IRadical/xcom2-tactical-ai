from src.game.game_state import GameState
from src.ai.evaluator import ActionEvaluator
import random

class CombatEngine:
    def __init__(self, game_state: GameState, verbose: bool = True):
        self.game_state = game_state
        self.evaluator = ActionEvaluator()
        self.verbose = verbose

    def resolve_shot(self, target) -> None:
        hit_roll = random.randint(1, 100)

        if hit_roll <= 70:
            damage = random.randint(3, 5)
            target.hp -= damage
            print(f"Hit! {target.name} takes {damage} damage (hp={target.hp})")
        else:
            print("Shot missed!")

    def run_turn (self) -> None:
        soldier = self.game_state.soldier
        action = self.evaluator.choose_best_action(self.game_state)

        print("\nAI decision:", action.action_type)

        if action.action_type == "shoot":
            target = next(
                enemy for enemy in self.game_state.enemies
                if enemy.name == action.target_name
            )

            if soldier.ammo > 0:
                soldier.ammo -= 1
                self.resolve_shot(target)

            elif action.action_type == "reload":
                soldier.ammo = 3
                print("Reloaded weapon")

            elif action.action_type == "move":
                soldier.position = action.destination
                print(f"Moved to position {action.destination}")
        
    def battle_over(self) -> bool:
        enemies_alive = [
            enemy for enemy in self.game_state.enemies
            if enemy.is_alive()
        ]

        return len(enemies_alive) == 0
