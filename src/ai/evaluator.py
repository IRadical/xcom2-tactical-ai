from __future__ import annotations

from src.game.actions import Action
from src.game.entities import Unit
from src.game.game_state import GameState
from src.game.geometry import (
    Position,
    elevation_delta,
    generate_neighbor_positions,
    manhattan_3d,
    within_grenade_radius,
)


class ActionEvaluator:
    def get_role_profile(self, soldier: Unit) -> dict[str, float]:
        profiles = {
            "assault": {
                "preferred_distance": 2,
                "close_range_bonus": 30,
                "long_range_bonus": 0,
                "survival_multiplier": 1.0,
                "flank_bonus": 70,
                "overwatch_bonus": 5,
                "heal_bonus": 0,
                "hunker_bonus": 8,
                "grenade_bonus": 25,
            },
            "sniper": {
                "preferred_distance": 5,
                "close_range_bonus": 0,
                "long_range_bonus": 30,
                "survival_multiplier": 1.2,
                "flank_bonus": 35,
                "overwatch_bonus": 30,
                "heal_bonus": 0,
                "hunker_bonus": 20,
                "grenade_bonus": 5,
            },
            "support": {
                "preferred_distance": 3,
                "close_range_bonus": 10,
                "long_range_bonus": 10,
                "survival_multiplier": 1.3,
                "flank_bonus": 40,
                "overwatch_bonus": 18,
                "heal_bonus": 60,
                "hunker_bonus": 25,
                "grenade_bonus": 15,
            },
        }
        return profiles.get(soldier.role, profiles["assault"])

    def has_line_of_sight(self, attacker: Unit, target: Unit) -> bool:
        dx = abs(attacker.position[0] - target.position[0])
        dy = abs(attacker.position[1] - target.position[1])
        dz = abs(attacker.position[2] - target.position[2])

        if dz > 1:
            return False
        if dx > 6 or dy > 6:
            return False

        return (dx + dy) <= 8

    def get_directional_cover_value(
        self,
        attacker_position: Position,
        target_position: Position,
        base_cover: int,
    ) -> int:
        if base_cover <= 0:
            return 0

        dx = attacker_position[0] - target_position[0]
        dy = attacker_position[1] - target_position[1]
        distance = manhattan_3d(attacker_position, target_position)

        if distance <= 2:
            return 0

        if abs(dx) > abs(dy):
            return base_cover
        if abs(dx) == abs(dy):
            return int(base_cover * 0.5)
        return int(base_cover * 0.25)

    def is_flanked(self, attacker: Unit, target: Unit) -> bool:
        if attacker.distance_to(target) > 2 or target.cover <= 0:
            return False

        effective_cover = self.get_directional_cover_value(
            attacker_position=attacker.position,
            target_position=target.position,
            base_cover=target.cover,
        )
        return effective_cover < target.cover

    def estimate_hit_chance(self, attacker: Unit, target: Unit) -> float:
        if not self.has_line_of_sight(attacker, target):
            return 0.0

        distance_penalty = attacker.distance_to(target) * 5
        effective_cover = self.get_directional_cover_value(
            attacker_position=attacker.position,
            target_position=target.position,
            base_cover=target.cover,
        )

        elevation = elevation_delta(attacker.position, target.position)
        elevation_bonus = 10 if elevation > 0 else 0
        elevation_penalty = 10 if elevation < 0 else 0

        raw_hit_chance = (
            attacker.aim
            - distance_penalty
            - effective_cover
            + elevation_bonus
            - elevation_penalty
        )
        return max(0.0, min(100.0, raw_hit_chance))

    def estimate_position_threat(
        self,
        soldier: Unit,
        enemies: list[Unit],
        position: Position,
        cover: int,
    ) -> float:
        total_threat = 0.0
        simulated_soldier = soldier.clone_at_position(position=position, cover=cover)

        for enemy in enemies:
            if not enemy.is_alive():
                continue
            if not self.has_line_of_sight(enemy, simulated_soldier):
                continue

            distance_penalty = enemy.distance_to(simulated_soldier) * 5
            effective_cover = self.get_directional_cover_value(
                attacker_position=enemy.position,
                target_position=position,
                base_cover=cover,
            )

            estimated_enemy_hit = enemy.aim - distance_penalty - effective_cover
            estimated_enemy_hit = max(0, min(100, estimated_enemy_hit))
            total_threat += estimated_enemy_hit / 100.0

        return total_threat

    def score_shot(self, soldier: Unit, enemy: Unit, enemies: list[Unit]) -> float:
        role = self.get_role_profile(soldier)
        hit_chance = self.estimate_hit_chance(soldier, enemy)
        distance = soldier.distance_to(enemy)

        kill_bonus = 180 if enemy.hp <= 4 else 0
        wounded_target_bonus = max(0, 12 - enemy.hp) * 8
        flank_bonus = role["flank_bonus"] if self.is_flanked(soldier, enemy) else 0
        close_range_bonus = role["close_range_bonus"] if distance <= 3 else 0
        long_range_bonus = role["long_range_bonus"] if distance >= 4 else 0

        low_accuracy_penalty = 80 if hit_chance < 25 else 40 if hit_chance < 35 else 0

        current_position_threat = self.estimate_position_threat(
            soldier=soldier,
            enemies=enemies,
            position=soldier.position,
            cover=soldier.cover,
        )

        threat_penalty = 0.0
        survival_multiplier = role["survival_multiplier"]
        if soldier.hp <= 4:
            threat_penalty = current_position_threat * 25 * survival_multiplier
        elif soldier.hp <= 7:
            threat_penalty = current_position_threat * 12 * survival_multiplier

        action_efficiency_bonus = 15 if soldier.action_points == 2 else 0

        return (
            (hit_chance * 2.0)
            + kill_bonus
            + wounded_target_bonus
            + close_range_bonus
            + long_range_bonus
            + flank_bonus
            + action_efficiency_bonus
            - low_accuracy_penalty
            - threat_penalty
        )

    def score_reload(self, soldier: Unit, best_hit_chance: float, enemies: list[Unit]) -> float:
        if soldier.action_points <= 0:
            return -100

        current_position_threat = self.estimate_position_threat(
            soldier=soldier,
            enemies=enemies,
            position=soldier.position,
            cover=soldier.cover,
        )

        if soldier.ammo == 0:
            return 100 - (current_position_threat * 10)

        if soldier.ammo == 1:
            return 8 - (current_position_threat * 8) if best_hit_chance < 15 else -35

        return -50

    def score_overwatch(
        self,
        soldier: Unit,
        visible_enemies: list[Unit],
        enemies: list[Unit],
    ) -> float:
        role = self.get_role_profile(soldier)

        if soldier.ammo <= 0 or soldier.action_points <= 0:
            return -100
        if not visible_enemies:
            return -20

        best_visible_hit = max(
            self.estimate_hit_chance(soldier, enemy)
            for enemy in visible_enemies
        )

        current_position_threat = self.estimate_position_threat(
            soldier=soldier,
            enemies=enemies,
            position=soldier.position,
            cover=soldier.cover,
        )

        return (
            10
            + (best_visible_hit * 0.8)
            + role["overwatch_bonus"]
            + (current_position_threat * 12)
            + (20 if soldier.hp <= 5 else 0)
        )

    def score_heal(
        self,
        soldier: Unit,
        allies: list[Unit],
        enemies: list[Unit],
    ) -> tuple[float, str | None]:
        role = self.get_role_profile(soldier)

        if soldier.role != "support":
            return -100, None
        if soldier.medkit_charges <= 0:
            return -100, None
        if soldier.action_points <= 0:
            return -100, None
        if soldier.ability_cooldowns.get("heal", 0) > 0:
            return -100, None

        valid_allies = [
            ally for ally in allies
            if ally.is_alive()
            and ally.hp < ally.max_hp
            and soldier.distance_to(ally) <= 2
        ]

        if not valid_allies:
            return -100, None

        def heal_priority(ally: Unit) -> float:
            missing_hp = ally.max_hp - ally.hp
            threat = self.estimate_position_threat(
                soldier=ally,
                enemies=enemies,
                position=ally.position,
                cover=ally.cover,
            )
            critical_bonus = 40 if ally.hp <= 4 else 0
            return missing_hp * 12 + threat * 20 + critical_bonus

        best_ally = max(valid_allies, key=heal_priority)
        return heal_priority(best_ally) + role["heal_bonus"], best_ally.name

    def score_hunker(self, soldier: Unit, enemies: list[Unit], best_hit_chance: float) -> float:
        role = self.get_role_profile(soldier)

        if soldier.hunkered_down or soldier.action_points <= 0:
            return -100

        current_position_threat = self.estimate_position_threat(
            soldier=soldier,
            enemies=enemies,
            position=soldier.position,
            cover=soldier.cover,
        )

        if current_position_threat < 0.60 and soldier.hp > 4:
            return -40

        low_hp_bonus = 45 if soldier.hp <= 4 else 18 if soldier.hp <= 7 else 0
        poor_shot_bonus = 18 if best_hit_chance < 20 else 8 if best_hit_chance < 30 else 0
        emergency_threat_bonus = 35 if current_position_threat >= 1.4 else 18 if current_position_threat >= 1.0 else 0

        return (
            -8
            + role["hunker_bonus"]
            + (current_position_threat * 22)
            + low_hp_bonus
            + poor_shot_bonus
            + emergency_threat_bonus
        )

    def get_cover_value_for_position(self, destination: Position) -> int:
        x, y, z = destination

        score = x + y + z
        if score % 5 == 0:
            return 40
        if score % 2 == 0:
            return 20
        return 0

    def score_move(
        self,
        soldier: Unit,
        enemies: list[Unit],
        destination: Position,
        current_best_hit_chance: float,
    ) -> float:
        if soldier.action_points == 1:
         return -20  
        
        if not enemies or soldier.action_points <= 0:
            return -100

        role = self.get_role_profile(soldier)

        closest_distance = min(
            manhattan_3d(destination, enemy.position)
            for enemy in enemies
        )

        preferred_distance = role["preferred_distance"]
        positioning_score = 30 - (abs(closest_distance - preferred_distance) * 5)

        cover_value = self.get_cover_value_for_position(destination)
        cover_bonus = cover_value * 0.9
        elevation_bonus = 12 if destination[2] > soldier.position[2] else 0

        movement_cost = manhattan_3d(soldier.position, destination) * 2

        survival_bonus = 0.0
        if soldier.hp <= 4:
            survival_bonus = cover_value * 1.6 * role["survival_multiplier"]
        elif soldier.hp <= 7:
            survival_bonus = cover_value * 0.9 * role["survival_multiplier"]

        shot_quality_bonus = 25 if current_best_hit_chance < 20 else 12 if current_best_hit_chance < 30 else 0

        simulated_soldier = soldier.clone_at_position(position=destination, cover=cover_value)
        simulated_soldier.action_points = max(0, soldier.action_points - 1)

        los_setup_bonus = 0.0
        flank_setup_bonus = 0.0

        for enemy in enemies:
            future_distance = simulated_soldier.distance_to(enemy)

            if future_distance <= 2 and enemy.cover > 0:
                effective_cover = self.get_directional_cover_value(
                    attacker_position=destination,
                    target_position=enemy.position,
                    base_cover=enemy.cover,
                )
                if effective_cover < enemy.cover:
                    flank_setup_bonus = max(flank_setup_bonus, 24)

            if self.has_line_of_sight(simulated_soldier, enemy):
                los_setup_bonus = max(
                    los_setup_bonus,
                    18 if soldier.action_points == 2 else 12,
                )

        destination_threat = self.estimate_position_threat(
            soldier=soldier,
            enemies=enemies,
            position=destination,
            cover=cover_value,
        )
        current_threat = self.estimate_position_threat(
            soldier=soldier,
            enemies=enemies,
            position=soldier.position,
            cover=soldier.cover,
        )

        threat_reduction_bonus = max(0.0, current_threat - destination_threat) * 40
        threat_penalty = destination_threat * 20 * role["survival_multiplier"]
        two_action_setup_bonus = 20 if soldier.action_points == 2 else 0

        return (
            positioning_score
            + cover_bonus
            + elevation_bonus
            + survival_bonus
            + shot_quality_bonus
            + flank_setup_bonus
            + los_setup_bonus
            + threat_reduction_bonus
            + two_action_setup_bonus
            - threat_penalty
            - movement_cost
        )

    def generate_move_actions(
        self,
        soldier: Unit,
        enemies: list[Unit],
        allies: list[Unit],
        current_best_hit_chance: float,
    ) -> list[Action]:
        actions: list[Action] = []
        occupied_positions = {enemy.position for enemy in enemies}
        occupied_positions.update({
            ally.position for ally in allies
            if ally.name != soldier.name
        })        
        for destination in generate_neighbor_positions(soldier.position):
            if destination in occupied_positions:
                continue
            actions.append(
                Action(
                    action_type="move",
                    destination=destination,
                    score=self.score_move(
                        soldier=soldier,
                        enemies=enemies,
                        destination=destination,
                        current_best_hit_chance=current_best_hit_chance,
                    ),
                )
            )

        return actions

    def get_grenade_candidates(
        self,
        soldier: Unit,
        enemies: list[Unit],
    ) -> list[tuple[Position, list[Unit]]]:
        if soldier.grenade_charges <= 0 or soldier.action_points <= 0:
            return []

        candidates: list[tuple[Position, list[Unit]]] = []
        seen_positions: set[Position] = set()
        grenade_range = 4

        for enemy in enemies:
            if not enemy.is_alive():
                continue
            if soldier.distance_to(enemy) > grenade_range:
                continue

            center = enemy.position
            if center in seen_positions:
                continue

            affected = [
                other_enemy
                for other_enemy in enemies
                if other_enemy.is_alive()
                and within_grenade_radius(center, other_enemy.position, radius=1)
            ]

            candidates.append((center, affected))
            seen_positions.add(center)

        return candidates

    def score_grenade(
        self,
        soldier: Unit,
        enemies_hit: list[Unit],
        visible_enemies: list[Unit],
    ) -> float:
        role = self.get_role_profile(soldier)

        if soldier.grenade_charges <= 0 or soldier.action_points <= 0:
            return -100
        if not enemies_hit:
            return -100

        enemies_hit_count = len(enemies_hit)
        kills_possible = sum(1 for enemy in enemies_hit if enemy.hp <= 3)
        enemies_in_cover = sum(1 for enemy in enemies_hit if enemy.cover > 0)
        wounded_bonus = sum(max(0, 6 - enemy.hp) * 5 for enemy in enemies_hit)
        cluster_bonus = 60 if enemies_hit_count >= 2 else 0
        cover_bonus = enemies_in_cover * 12

        if enemies_in_cover >= 1:
            cover_bonus += 25

        best_visible_hit = 0.0
        if visible_enemies:
            best_visible_hit = max(
                self.estimate_hit_chance(soldier, enemy)
                for enemy in visible_enemies
            )

        shot_already_good_penalty = 45 if best_visible_hit >= 65 else 20 if best_visible_hit >= 50 else 0
        single_target_penalty = 35 if enemies_hit_count == 1 and kills_possible == 0 and enemies_in_cover == 0 else 0
        scarcity_penalty = 25 if soldier.grenade_charges == 1 else 0

        return (
            (kills_possible * 140)
            + (enemies_hit_count * 28)
            + wounded_bonus
            + cluster_bonus
            + cover_bonus
            + role["grenade_bonus"]
            - shot_already_good_penalty
            - single_target_penalty
            - scarcity_penalty
        )

    def choose_best_action(self, game_state: GameState) -> Action:
        soldier = game_state.soldier
        enemies = game_state.living_enemies()
        allies = game_state.living_soldiers()

        if not enemies or soldier.action_points <= 0:
            return Action(action_type="wait", score=0)

        visible_enemies = [
            enemy for enemy in enemies
            if self.has_line_of_sight(soldier, enemy)
        ]

        shot_actions: list[Action] = []
        if soldier.action_points == 2 and shot_actions:
            best_shot = max(shot_actions, key=lambda a: a.score)
            if best_shot.score > 20:
                return best_shot
            
        if soldier.ammo > 0:
            for enemy in visible_enemies:
                shot_actions.append(
                    Action(
                        action_type="shoot",
                        target_name=enemy.name,
                        score=self.score_shot(soldier, enemy, enemies),
                    )
                )

        best_hit_chance = 0.0
        if visible_enemies:
            best_hit_chance = max(
                self.estimate_hit_chance(soldier, enemy)
                for enemy in visible_enemies
            )

        if soldier.action_points == 2 and best_hit_chance < 30:
            move_actions = self.generate_move_actions(
                soldier,
                enemies,
                allies,
                best_hit_chance
            )

            best_move = max(move_actions, key=lambda a: a.score, default=None)

            if best_move and best_move.score > 0:
                return best_move

        grenade_actions: list[Action] = []
        for target_position, enemies_hit in self.get_grenade_candidates(soldier, enemies):
            grenade_actions.append(
                Action(
                    action_type="grenade",
                    target_position=target_position,
                    score=self.score_grenade(soldier, enemies_hit, visible_enemies),
                )
            )

        heal_score, heal_target_name = self.score_heal(soldier, allies, enemies)

        possible_actions: list[Action] = []
        possible_actions.extend(shot_actions)
        possible_actions.extend(grenade_actions)
        self.generate_move_actions(
            soldier,
            enemies,
            allies,  
            best_hit_chance
        )
        possible_actions.append(Action("reload", self.score_reload(soldier, best_hit_chance, enemies)))
        possible_actions.append(Action("overwatch", self.score_overwatch(soldier, visible_enemies, enemies)))
        possible_actions.append(Action("heal", heal_score, target_name=heal_target_name))
        possible_actions.append(Action("hunker", self.score_hunker(soldier, enemies, best_hit_chance)))

        return max(possible_actions, key=lambda action: action.score)