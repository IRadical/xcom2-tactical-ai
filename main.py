from src.ai.evaluator import ActionEvaluator
from src.game.entities import Unit
from src.game.game_state import GameState

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
        Unit("Sectoid", 4, 65, 2, 5, True),
        Unit("Trooper", 6, 60, 3, 6, True)
    ]

    game_state = GameState(soldier, enemies)

    evaluator = ActionEvaluator()

    best_action = evaluator.choose_best_action(game_state)

    print("Action selected by AI:")
    print("Type", best_action.action_type)
    print("Target:", best_action.target_name)

if __name__ == "__main__":
    main()