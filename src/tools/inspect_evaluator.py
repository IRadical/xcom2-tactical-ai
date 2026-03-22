import inspect

from src.ai.evaluator import ActionEvaluator


def main() -> None:
    print("ActionEvaluator:", ActionEvaluator)
    print("ActionEvaluator.__init__:", inspect.signature(ActionEvaluator))

    if hasattr(ActionEvaluator, "choose_best_action"):
        print("choose_best_action:", inspect.signature(ActionEvaluator.choose_best_action))


if __name__ == "__main__":
    main()