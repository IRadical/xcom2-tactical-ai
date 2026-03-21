import random
from src.simulation.combat_analytics import CombatAnalytics

def run_seeded_simulation(battles: int, seed: int) -> dict:
    random.seed(seed)
    analytics = CombatAnalytics()
    return analytics.run_simulation(battles)

def test_ai_baseline_regression_guard() -> None:
    results = run_seeded_simulation(battles=200, seed=42)

    assert results["win_rate"] >= 0.75, (
        f"Win rate regression detected: {results['win_rate']:.2%}"
    )
    assert results["avg_turns"] <= 11.0, (
        f"Average turns too high: {results['avg_turns']:.2f}"
    )
    assert results["avg_damage_taken"] <= 6.8, (
        f"Damage tanken regression detected: {results['avg_damage_taken']:.2f}"
    )
    assert results["avg_kills"] >= 2.6, (
        f"Kills to low: {results['avg_kills']:.2f}"
    )