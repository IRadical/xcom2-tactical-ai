import random
from src.simulation.combat_analytics import CombatAnalytics

def run_seeded_simulation(battles: int, seed: int) -> dict:
    random.seed(seed)
    analytics = CombatAnalytics()
    return analytics.run_simulation(battles)

def test_seeded_simulation_is_repeatable() -> None:
    first = run_seeded_simulation(battles=100, seed=123)
    second = run_seeded_simulation(battles=100, seed=123)

    assert first == second, "Seeded simulation should be deterministic"