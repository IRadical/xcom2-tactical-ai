from src.simulation.combat_engine import CombatEngine
from src.game.entities import Unit
from src.game.game_state import GameState
import random


class CombatAnalytics:
    def run_single_battle(self) -> dict:
        soldier = Unit(
            name="Ranger",
            hp=10,
            aim=75,
            ammo=3,
            position=0,
            is_enemy=False,
            cover=0,
        )

        enemies = [
            Unit("Sectoid", random.randint(4, 6), 65, 2, random.randint(4, 7), True,
                 cover=random.choice([0,20])),
            Unit("Trooper", random.randint(5, 7), 60, 3, random.randint(5, 9), True,
                 cover=random.choice([0,20]))
        ]

        game_state = GameState(soldier, enemies)
        engine = CombatEngine(game_state, verbose=False)

        turn = 0
        max_turns = 15

        while not engine.battle_over() and turn < max_turns:
            engine.run_turn()
            turn += 1

        enemies_alive = [enemy for enemy in enemies if enemy.is_alive()]
        metrics = engine.metrics

        return {
            "win": len(enemies_alive) == 0 and soldier.hp > 0,
            "turns": turn,
            "soldier_hp": soldier.hp,
            "shots_fired": metrics["shots_fired"],
            "shots_hit": metrics["shots_hit"],
            "damage_dealt": metrics["damage_dealt"],
            "damage_taken": metrics["damage_taken"],
            "kills": metrics["kills"],
            "action_counts": metrics["action_counts"]
        }

    def run_simulation(self, battles: int = 100) -> dict:
        wins = 0
        total_turns = 0
        total_hp = 0
        total_shots_fired = 0
        total_shots_hit = 0
        total_damage_dealt = 0
        total_damage_taken = 0
        total_kills = 0

        total_actions_counts = {
            "shoot": 0,
            "reload": 0,
            "move": 0,
            "wait": 0,
        }

        for _ in range(battles):
            result = self.run_single_battle()

            if result["win"]:
                wins += 1

            total_turns += result["turns"]
            total_hp += result["soldier_hp"]
            total_shots_fired += result["shots_fired"]
            total_shots_hit += result["shots_hit"]
            total_damage_dealt += result["damage_dealt"]
            total_damage_taken  += result["damage_taken"]
            total_kills += result["kills"]

            for action_name, count in result["action_counts"].items():
                total_actions_counts[action_name] += count
            
        accuracy = 0.0
        if total_shots_fired > 0:
            accuracy = total_shots_hit / total_shots_fired           

        return {
            "battles": battles,
            "win_rate": wins / battles,
            "avg_turns": total_turns / battles,
            "avg_hp_remaining": total_hp / battles,
            "accuracy": accuracy,
            "avg_damage_dealt": total_damage_dealt / battles,
            "avg_damage_taken": total_damage_taken / battles,
            "avg_kills": total_kills / battles,
            "action_counts": total_actions_counts,
        }
