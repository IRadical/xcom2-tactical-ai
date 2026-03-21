from __future__ import annotations

import random

from src.game.entities import Unit
from src.game.game_state import GameState
from src.simulation.combat_engine import CombatEngine


class CombatAnalytics:
    def run_single_battle(self) -> dict:
        soldiers = [
            Unit(
                name="Assault-1",
                hp=10,
                aim=75,
                ammo=5,
                position=(0, 0, 0),
                is_enemy=False,
                cover=0,
                role="assault",
                max_hp=10,
                medkit_charges=0,
                grenade_charges=1,
            ),
            Unit(
                name="Sniper-1",
                hp=9,
                aim=80,
                ammo=5,
                position=(0, 1, 1),
                is_enemy=False,
                cover=0,
                role="sniper",
                max_hp=9,
                medkit_charges=0,
                grenade_charges=0,
            ),
            Unit(
                name="Support-1",
                hp=10,
                aim=68,
                ammo=5,
                position=(0, 2, 0),
                is_enemy=False,
                cover=0,
                role="support",
                max_hp=10,
                medkit_charges=2,
                grenade_charges=1,
            ),
        ]

        enemies = [
            Unit(
                name="Sectoid",
                hp=random.randint(4, 6),
                aim=65,
                ammo=2,
                position=(random.randint(3, 6), random.randint(0, 3), random.choice([0, 1])),
                is_enemy=True,
                cover=random.choice([0, 20]),
                role="assault",
                max_hp=6,
            ),
            Unit(
                name="Trooper",
                hp=random.randint(5, 7),
                aim=60,
                ammo=3,
                position=(random.randint(4, 8), random.randint(1, 4), random.choice([0, 1])),
                is_enemy=True,
                cover=random.choice([0, 20]),
                role="assault",
                max_hp=7,
            ),
            Unit(
                name="StunLancer",
                hp=random.randint(5, 7),
                aim=62,
                ammo=3,
                position=(random.randint(5, 8), random.randint(0, 4), random.choice([0, 1])),
                is_enemy=True,
                cover=random.choice([0, 20]),
                role="assault",
                max_hp=7,
            ),
        ]

        game_state = GameState(soldiers, enemies)
        engine = CombatEngine(game_state, verbose=False)

        turn = 0
        max_turns = 15

        while not engine.battle_over() and turn < max_turns:
            engine.run_turn()
            turn += 1

        soldiers_alive = [s for s in soldiers if s.is_alive()]
        enemies_alive = [e for e in enemies if e.is_alive()]
        metrics = engine.metrics

        return {
            "win": len(enemies_alive) == 0 and len(soldiers_alive) > 0,
            "turns": turn,
            "soldier_hp": sum(s.hp for s in soldiers_alive),
            "shots_fired": metrics["shots_fired"],
            "shots_hit": metrics["shots_hit"],
            "damage_dealt": metrics["damage_dealt"],
            "damage_taken": metrics["damage_taken"],
            "kills": metrics["kills"],
            "grenades_used": metrics["grenades_used"],
            "action_counts": metrics["action_counts"],
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
        total_grenades_used = 0

        total_action_counts = {
            "shoot": 0,
            "reload": 0,
            "move": 0,
            "wait": 0,
            "overwatch": 0,
            "heal": 0,
            "hunker": 0,
            "grenade": 0,
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
            total_damage_taken += result["damage_taken"]
            total_kills += result["kills"]
            total_grenades_used += result["grenades_used"]

            for action_name, count in result["action_counts"].items():
                total_action_counts[action_name] += count

        accuracy = total_shots_hit / total_shots_fired if total_shots_fired > 0 else 0

        return {
            "battles": battles,
            "win_rate": wins / battles,
            "avg_turns": total_turns / battles,
            "avg_hp_remaining": total_hp / battles,
            "accuracy": accuracy,
            "avg_damage_dealt": total_damage_dealt / battles,
            "avg_damage_taken": total_damage_taken / battles,
            "avg_kills": total_kills / battles,
            "avg_grenades_used": total_grenades_used / battles,
            "action_counts": total_action_counts,
        }