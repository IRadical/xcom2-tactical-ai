from src.game.game_state import GameState
from src.ai.evaluator import ActionEvaluator
import random

class CombatEngine:
    def __init__(self, game_state: GameState, verbose: bool = True):
        self.game_state = game_state
        self.evaluator = ActionEvaluator()
        self.verbose = verbose

    def resolve_shot(self, attacker, target) -> None:
        hit_roll = random.randint(1, 100)

        hit_chance = attacker.aim

        if hit_roll <= hit_chance:
            damage = random.randint(2, 4)
            target.hp -= damage
            target.hp = max(0, target.hp)

            if self.verbose:
                print(f"{attacker.name} hits {target.name} for {damage} damage (hp={target.hp})")

        else:

            if self.verbose:
                print(f"{attacker.name} missed {target.name}")

    def player_turn(self):
        soldier = self.game_state.soldier
        action = self.evaluator.choose_best_action(self.game_state)

        if self.verbose:
            print("\nAI decision:", action.action_type)
        
        if action.action_type == "shoot":
            targets = [
                enemy for enemy in self.game_state.enemies
                if enemy.is_alive() and enemy.name == action.target_name
            ]

            if targets and soldier.ammo > 0:
                soldier.ammo -= 1
                self.resolve_shot(soldier, targets[0])
        
        elif action.action_type == "reload":
            soldier.amoo = 3

            if self.verbose:
                print ("Soldier reloads weapon")
            
        elif action.action_type == "move":
            soldier.position = action.destination

            if self.verbose:
                print(f"Soldier moves to {action.destination}")
    
    def enemy_turn(self):
        soldier = self.game_state.soldier

        for enemy in self.game_state.enemies:
            
            if not enemy.is_alive():
                continue
            
            if self.verbose:
                print(f"{enemy.name} attacks")
            
            self.resolve_shot(enemy, soldier)

            if soldier.hp <= 0:
                if self.verbose:
                    print("Soldier has been eliminated")
                return
            

    def run_turn (self):
       self.player_turn()

       if self.game_state.soldier.hp <= 0:
           return
       
       self.enemy_turn()
        
    def battle_over(self) -> bool:
        soldier_alive = self.game_state.soldier.hp > 0
        enemies_alive = [
            enemy for enemy in self.game_state.enemies
            if enemy.is_alive()
        ]

        return not soldier_alive or len(enemies_alive) == 0
