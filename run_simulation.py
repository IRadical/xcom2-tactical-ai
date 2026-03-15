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


if __name__ == "__main__":
    main()
