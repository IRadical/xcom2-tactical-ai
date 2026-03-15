from src.game.entities import Unit
from src.game.game_state import GameState
from src.simulation.combat_engine import CombatEngine

def main():
    soldier = Unit(
        name="Ranger",
        hp=10,
        aim=75,
        ammo=3,
        position=0,
        is_enemy=False
    )

    enemies = [
        Unit("Sectoid", 5, 65, 2, 5, True),
        Unit("Trooper", 6, 60, 3, 7, True)
    ]

    game_state = GameState(soldier, enemies)
    engine = CombatEngine(game_state)

    turn = 1

    while not engine.battle_over():
        print("\n----- TURN", turn, "-----")

        engine.run_turn()

        turn += 1
        
        if turn > 10:
            break

        print("\nTurn ended")
   
   
if __name__ == "__main__":
    main()