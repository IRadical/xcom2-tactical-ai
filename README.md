Markdown
# XCOM 2 TACTICAL AI BRIDGE

A Python-based tactical AI system for XCOM-style turn-based combat, now extended with a live integration bridge to **XCOM 2: WAR OF THE CHOSEN**.

The project started as a utility-based tactical decision system in Python and has evolved into a hybrid architecture that:
* **SIMULATES** tactical combat in Python.
* **EVALUATES** battlefield decisions with a scoring model.
* **READS** real tactical state exported from **XCOM 2** through a custom mod.
* **PREPARES** game-state data for real in-game decision-making.

---

## OVERVIEW

This project explores how an AI agent can make tactical decisions in a turn-based combat environment inspired by XCOM. 

Instead of choosing actions randomly, the system evaluates the battlefield state and scores possible actions based on **HEURISTICS** such as:
* Offense and hit probability.
* Movement opportunities and flanking.
* Ammunition and action point management.
* Unit positioning and tactical context.

The project now features **TWO COMPLEMENTARY LAYERS**:

1.  **PYTHON TACTICAL AI CORE**: A standalone combat simulator and evaluator for XCOM-style decisions.
2.  **XCOM 2 INTEGRATION BRIDGE**: A mod + parser pipeline that exports tactical state from XCOM 2 and converts it into Python `GameState` objects.

---

## CURRENT CAPABILITIES

### 🛡️ PYTHON TACTICAL AI
* Utility-based action evaluation.
* Tactical combat simulation.
* Action scoring for shooting, moving, reloading, overwatch, and grenades.
* Structured **UNIT** and **GAMESTATE** models.

### 🛰️ XCOM 2 BRIDGE
* Detects **TACTICAL HUD** runtime from the game.
* Exports live tactical battlefield snapshots from **XCOM 2 WOTC**.
* Parses combat state from `Launch.log`.
* Detects the **ACTIVE SOLDIER** and parses legal movement tiles.
* Runs the evaluator on real in-game state.
* Produces exportable decision strings.

---

## PROJECT ARCHITECTURE

```text
SRC/
├── AI/
│   └── evaluator.py                # AI SCORING LOGIC AND ACTION SELECTION
├── GAME/
│   ├── actions.py                  # ACTION MODELS
│   ├── entities.py                 # UNIT MODEL
│   ├── game_state.py               # BATTLEFIELD STATE MODEL
│   └── geometry.py                 # POSITION TYPING / GEOMETRY HELPERS
├── INTEGRATION/
│   ├── xcom_log_bridge.py          # READS TACTICAL SNAPSHOTS FROM XCOM 2 LOGS
│   ├── xcom_state_adapter.py       # CONVERTS LOG DATA INTO PYTHON MODELS
│   ├── xcom_action_formatter.py    # FORMATS ACTIONS INTO EXPORTABLE STRINGS
│   └── xcom_decision_bridge.py     # END-TO-END BRIDGE: LOG -> AI -> ACTION
├── SIMULATION/
│   ├── combat_engine.py            # TACTICAL COMBAT SIMULATION ENGINE
│   └── combat_analytics.py         # METRICS AND COMBAT STATISTICS
└── VISUALIZATION/
    ├── simulate_battle.py          # SIMULATION RUNNER
    └── tactical_renderer.py        # TACTICAL RENDERING HELPERS
```
TECH STACK
PYTHON: 3.X, NUMPY for analytics, Pytest-style validation scripts.

GAME INTEGRATION: UNREALSCRIPT (XCOM 2 WOTC SDK), MODBUDDY.

WORKFLOW: Live log parsing and structured world-state export.

CURRENT STATUS
🟢 TACTICAL AI CORE
STABLE. Utility-based decision logic and structured modeling are fully functional.

🟡 XCOM 2 INTEGRATION
WORKING PROTOTYPE. Live export and parsing are implemented.

CURRENT LIMITATION: The AI currently lacks full offensive context from the real game (Visibility/LOS, real hit chances, and target cover). Because of this, the evaluator may choose conservative actions like OVERWATCH as a fallback.

HOW TO RUN
RUN SIMULATION
Bash
```python main.py```
TEST THE XCOM 2 BRIDGE PARSER
Bash
```python -m tests.test_xcom_bridge```
RUN AI DECISION OVER REAL XCOM 2 STATE
Bash
```python -m tests.test_xcom_decision_bridge```

NEXT MILESTONES

🔴 HIGH PRIORITY
EXPORT visible targets and real hit chances from XCOM 2.

EXPORT target cover and flanking states.

IMPLEMENT a command channel to write actions back to the game.

🔵 MEDIUM PRIORITY
Improve movement selection using real legal tiles.

Integrate LINE-OF-SIGHT (LOS) calculations into the evaluator.

AUTHOR
Developed as a portfolio project focused on TACTICAL AI, DECISION SYSTEMS, and GAME INTEGRATION.
