from src.simulation.combat_analytics import CombatAnalytics


def main():
    analytics = CombatAnalytics()
    results = analytics.run_simulation(100)

    print("\nSIMULATION RESULTS")
    print("-----------------------")
    print("Battles:", results["battles"])
    print("Win rate:", round(results["win_rate"] * 100, 2), "%")
    print("Average turns:", round(results["avg_turns"], 2))
    print("Average HP remaining:", round(results["avg_hp_remaining"], 2))
    print("Accuracy:", round(results["accuracy"] * 100, 2), "%")
    print("Average damage dealt:", round(results["avg_damage_dealt"], 2))
    print("Average damage taken:", round(results["avg_damage_taken"], 2))
    print("Average kills:", round(results["avg_kills"], 2))
    print("Average grenades used:", round(results["avg_grenades_used"], 2))

    print("\nACTION DISTRIBUTION")
    print("---------------------")
    for action_name, count in results["action_counts"].items():
        print(f"{action_name}: {count}")


if __name__ == "__main__":
    main()