import inspect

from src.game.entities import Unit
from src.game.game_state import GameState


def main() -> None:
    print("Unit.__init__ signature:")
    print(inspect.signature(Unit))

    print()
    print("GameState.__init__ signature:")
    print(inspect.signature(GameState))


if __name__ == "__main__":
    main()