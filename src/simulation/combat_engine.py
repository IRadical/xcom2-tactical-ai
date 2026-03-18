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
            "shots_hit" : 0,
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
        distance = attacker.distance_to(target)
        distance_penalty = distance * 5
        hit_chance = attacker.aim - distance_penalty - target.cover
        hit_chance = max(0, min(100, hit_chance))

        hit_roll = random.randint(1, 100)

        if attacker.is_enemy:
            self.metrics["damage_taken"] += 0
        else:
            self.metrics["shots_fired"] +=1

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
                    f"{attacker.name} hits {target.name} for {damage} damage"
                    f"(hp={target.hp}, target cover={target.cover}, hit chance={hit_chance})"
                )
        else:
            if self.verbose:
                print(
                    f"{attacker.name} missed {target.name}"
                    f"(target cover={target.cover}, hit chance={hit_chance})"
                )

    def player_turn(self) -> None:
        soldier = self.game_state.soldier
        action = self.evaluator.choose_best_action(self.game_state)

        if action.action_type in self.metrics["action_counts"]:
            self.metrics["action_counts"][action.action_type] += 1

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
            soldier.amoo = 6

            if self.verbose:
                print ("Soldier reloads weapon")
            
        elif action.action_type == "move":
            soldier.position = action.destination
            soldier.cover = self.evaluator.get_cover_value_for_position(action.destination)

            if self.verbose:
                print(f"Soldier moves to {action.destination} and gains cover {soldier.cover}")
    
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
