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
    print("Type:", best_action.action_type)
    print("Target:", best_action.target_name)
    print("Destination:", best_action.destination)
    print("Score:", best_action.score)

    print("\nEnemy analysis:")
    for enemy in enemies:
        hit_chance = evaluator.estimate_hit_chance(soldier, enemy)
        distance = soldier.distance_to(enemy)
        print(f"{enemy.name} -> distance: {distance}, estimated hit chance: {hit_chance}")

    print("\nMovement analysys:")
    for action in evaluator.generate_movement_actions(soldier, enemies):
        print(f"Move to {action.destination} -> score: {action.score}")
if __name__ == "__main__":
    main()