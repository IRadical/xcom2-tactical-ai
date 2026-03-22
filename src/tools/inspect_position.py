from src.game.geometry import Position


def main() -> None:
    print("Position type:", type(Position))
    print("Position repr:", Position)
    print("Position dir:", [x for x in dir(Position) if not x.startswith("__")])

    try:
        p = Position(1, 2, 3)
        print("Constructed Position(1,2,3):", p)
    except Exception as e:
        print("Error constructing Position(1,2,3):", repr(e))

    try:
        p = Position(x=1, y=2, z=3)
        print("Constructed Position(x=1,y=2,z=3):", p)
    except Exception as e:
        print("Error constructing Position(x=1,y=2,z=3):", repr(e))


if __name__ == "__main__":
    main()