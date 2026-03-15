from src.simulation.combat_engine import CombatEngine
from src.game.entities import Unit
from src.game.game_state import GameState
import random

class CombatAnalytics:
    def run_single_battle(self):
        soldier = Unit(
            name="Ranger",
            hp=10,
            aim=75,
            ammo=3,
            position=0,
            is_enemy=False
        )

        enemies = [
            Unit("Sectoid", random.randint(4,6), 65, 2, random.randint(4,7), True),
            Unit("Trooper", random.randint(5,7), 65, 2, random.randint(5,9), True)            
        ]
        
        game_state = GameState(soldier, enemies)
        engine = CombatEngine(game_state)

        turn = 0

        while not engine.battle_over():
            engine.run_turn()
            turn += 1

            if turn > 15:
                break

            enemies_alive = [enemy for enemy in enemies if enemy.is_alive()]

            return {
                "win": len(enemies_alive) == 0,
                "turns": turn,
                "soldier_hp": soldier.hp
            }
    def run_simulation(self, battles = 100):
        wins = 0
        total_turns = 0
        total_hp = 0

        for i in range(battles):
            result = self.run_single_battle()

            if result["win"]:
                wins += 1

            total_turns += result["turns"]
            total_hp += result["soldier_hp"]

        return{
        "battles": battles,
        "win_rate": wins / battles,
        "avg_turns": total_turns / battles,
        "avg_hp_remaining": total_hp / battles        
        }