import random

from src.simulation.combat_analytics import CombatAnalytics


def main() -> None:
    seed = 42
    battles = 200

    random.seed(seed)
    analytics = CombatAnalytics()
    results = analytics.run_simulation(battles)

    print("\nAI VALIDATION RESULTS")
    print("-----------------------")
    print("Seed:", seed)
    print("Battles:", results["battles"])
    print("Win rate:", round(results["win_rate"] * 100, 2), "%")
    print("Average turns:", round(results["avg_turns"], 2))
    print("Average HP remaining:", round(results["avg_hp_remaining"], 2))
    print("Accuracy:", round(results["accuracy"] * 100, 2), "%")
    print("Average damage dealt:", round(results["avg_damage_dealt"], 2))
    print("Average damage taken:", round(results["avg_damage_taken"], 2))
    print("Average kills:", round(results["avg_kills"], 2))

    avg_grenades_used = results.get("avg_grenades_used")
    if avg_grenades_used is not None:
        print("Average grenades used:", round(avg_grenades_used, 2))

    print("\nACTION DISTRIBUTION")
    print("---------------------")
    for action_name, count in results["action_counts"].items():
        print(f"{action_name}: {count}")

    print("\nVALIDATION GATES")
    print("---------------------")

    gates = {
        "win_rate >= 75%": results["win_rate"] >= 0.75,
        "avg_turns <= 11.0": results["avg_turns"] <= 11.0,
        "avg_damage_taken <= 6.8": results["avg_damage_taken"] <= 6.8,
        "avg_kills >= 2.6": results["avg_kills"] >= 2.6,
    }

    passed_all = True
    for gate_name, passed in gates.items():
        status = "PASS" if passed else "FAIL"
        print(f"{gate_name}: {status}")
        if not passed:
            passed_all = False

    print("\nFINAL STATUS")
    print("---------------------")
    print("FUNCTIONAL BASELINE READY" if passed_all else "NEEDS MORE STABILIZATION")


if __name__ == "__main__":
    main()