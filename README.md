# Tactical AI Decision System (XCOM-style Combat)

A Python-based AI agent exploring tactical decision-making and game state evaluation, inspired by the mechanics of XCOM-style turn-based combat.

The goal of this project is to build an intelligent agent capable of analyzing complex combat scenarios, evaluating multiple lines of action, and selecting the optimal move based on a **Utility-based Scoring Model**.

---

## 🚀 Key Features

**Action Evaluation System**  
A logic engine that weights options such as shooting, moving, or reloading.

**Probability Estimation**  
Dynamic calculation of hit chance based on game state variables.

**Combat Simulation**  
A core engine that processes turn-based events, damage, and entity health.

**Scoring-based Selection**  
The AI prioritizes actions with the highest tactical value rather than random selection.

---

## 🏗️ Project Architecture

The codebase follows **Object-Oriented Design (OOD)** principles to ensure the AI logic is decoupled from the game rules.

```text
src/
 ├── ai/
 │   └── evaluator.py        # The "Brain": Scoring logic and decision making.
 ├── game/
 │   ├── actions.py          # Action definitions (Shoot, Move, Reload).
 │   ├── entities.py         # Unit modeling (Soldiers, Aliens, Stats).
 │   └── game_state.py       # Snapshot of the current battlefield.
 └── engine/
     └── combat_engine.py    # Turn processor and event resolution.
```
💻 Tech Stack

Python 3.x

Pytest

📈 Project Status & Roadmap

This project is currently in the Core Logic Development Phase.

 Basic combat simulation and turn flow

 Action scoring (Utility) system

 AI agent decision-making logic

Planned improvements:

 Cover evaluation and tactical positioning

 Flanking logic and multi-enemy scenarios

 External integration with a tactical game environment

🧠 Technical Motivation

This project focuses on exploring core challenges in game AI:

Tactical AI Systems
Modeling intelligent behavior in environments with high uncertainty (RNG).

Software Architecture
Maintaining a clear separation between Perception (Game State) and Decision (Evaluator).

Utility Algorithms
Using heuristic scoring systems to drive decision-making in strategy games.

🔧 How to Run

To see the AI decision logs in the terminal:

python main.py

Example Output
----- TURN 1 -----

AI decision: shoot
Hit! Sectoid takes 5 damage (hp=0)

Battle ended

----- TURN 2 -----

AI decision: shoot
Hit! Trooper takes 3 damage (hp=3)

Battle ended

----- TURN 3 -----

AI decision: shoot
Hit! Trooper takes 4 damage (hp=-1)

Battle ended

AI decision: shoot
Hit! Sectoid takes 4 damage (hp=1)

Battle ended
```
