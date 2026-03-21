# Tactical AI Decision System (XCOM-Style Combat)

A Python-based AI agent focused on tactical decision-making and game state evaluation, inspired by the mechanics of XCOM-style turn-based combat.

The purpose of this project is to build an intelligent agent capable of analyzing combat scenarios, evaluating multiple possible actions, and selecting the most effective move using a **utility-based scoring model**.

---

## Overview

This project explores how an AI can make decisions in a turn-based tactical environment by scoring available actions such as attacking, moving, or reloading.

Instead of choosing randomly, the agent evaluates the current battlefield state and prioritizes the action with the highest tactical value.

---

## Key Features

### Action Evaluation System
A decision-making engine that scores available actions such as shooting, moving, and reloading.

### Probability Estimation
Dynamic hit chance calculation based on combat context and game state conditions.

### Combat Simulation
A simulation core that handles turn flow, damage resolution, and unit health updates.

### Scoring-Based Selection
The AI selects actions based on tactical utility rather than random behavior.

---

## Project Architecture

The codebase follows **Object-Oriented Design (OOD)** principles to keep decision logic separated from game rules and combat execution.

```text
src/
 ├── ai/
 │   └── evaluator.py        # AI scoring logic and decision-making
 ├── game/
 │   ├── actions.py          # Action definitions (Shoot, Move, Reload)
 │   ├── entities.py         # Unit models (Soldiers, Aliens, Stats)
 │   └── game_state.py       # Current battlefield snapshot
 └── engine/
     └── combat_engine.py    # Turn processing and event resolution
```

---

## Tech Stack

- Python 3.x
- Pytest

---

## Project Status

This project is currently in the **Core Logic Development Phase**.

### Implemented

- Basic combat simulation and turn flow
- Utility-based action scoring
- AI agent decision-making logic

### Planned Improvements

- Cover evaluation and tactical positioning
- Flanking logic and multi-enemy scenarios
- Integration with an external tactical game environment

---

## Technical Motivation

This project explores key challenges in game AI development.

### Tactical AI Systems

Modeling intelligent behavior in environments with uncertainty and probability-based outcomes.

### Software Architecture

Maintaining a clear separation between **Perception (Game State)** and **Decision-Making (Evaluator)**.

### Utility Algorithms

Applying heuristic scoring systems to drive decision-making in tactical strategy environments.

---

## How to Run

Run the following command to execute the simulation and see the AI decisions in the terminal:

```bash
python main.py
```

---

## Example Output

```text
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

---

## Future Goals

The long-term goal is to evolve this project into a more advanced tactical AI system capable of handling:

- Positioning strategy
- Threat analysis
- Multi-target evaluation
- Advanced combat heuristics
- Integration with a tactical simulation or game environment

---

## Author

Developed as a portfolio project focused on **Game AI, Decision Systems, and Tactical Simulation using Python**.
