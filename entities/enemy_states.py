"""Finite state machine for enemy behavior.

Each state is a small class with enter / update / exit. ``update`` returns the
name of the next state to switch to, or ``None`` to stay. The Enemy owns the
current state and exposes the movement/sensing helpers the states rely on.

    Patrol --(see player)--> Chase --(close)--> Attack
       ^                       |                  |
       |                       v                  v
    Return <---(timeout)--- Search <--(lost)------+
"""

from panda3d.core import Vec3
from config import (
    ENEMY_SPEED, ENEMY_CHASE_SPEED, ENEMY_DETECT_RANGE, ENEMY_LOSE_RANGE,
    ENEMY_ATTACK_RANGE, ENEMY_ATTACK_WINDUP, ENEMY_ATTACK_LUNGE_SPEED,
    ENEMY_ATTACK_LUNGE_TIME, ENEMY_ATTACK_COOLDOWN, ENEMY_SEARCH_TIME,
)


class State:
    name = "state"

    def __init__(self, enemy):
        self.enemy = enemy
        self.t = 0.0

    def enter(self):
        self.t = 0.0

    def update(self, dt, player_pos):
        return None

    def exit(self):
        pass


class Patrol(State):
    """Wander to random points inside the home room."""
    name = "patrol"

    def enter(self):
        super().enter()
        self.enemy.pick_patrol_target()

    def update(self, dt, player_pos):
        if self.enemy.player_dist(player_pos) < ENEMY_DETECT_RANGE:
            return "chase"
        remaining = self.enemy.move_toward(self.enemy.patrol_target, ENEMY_SPEED, dt)
        if remaining < 0.5:
            self.enemy.pick_patrol_target()
        return None


class Chase(State):
    """Run the player down, remembering where they were last seen."""
    name = "chase"

    def update(self, dt, player_pos):
        dist = self.enemy.player_dist(player_pos)
        self.enemy.remember(player_pos)
        if dist <= ENEMY_ATTACK_RANGE:
            return "attack"
        if dist > ENEMY_LOSE_RANGE:
            return "search"
        self.enemy.move_toward(player_pos, ENEMY_CHASE_SPEED, dt)
        return None


class Attack(State):
    """Telegraphed lunge: brief wind-up (flash), then dash, then recover."""
    name = "attack"

    def enter(self):
        super().enter()
        self.phase = "windup"
        self.lunge_dir = Vec3(0, 0, 0)
        self.enemy.node.setColorScale(1.8, 1.8, 1.8, 1)   # telegraph

    def update(self, dt, player_pos):
        self.t += dt

        if self.phase == "windup":
            self.enemy.face(player_pos)
            if self.t >= ENEMY_ATTACK_WINDUP:
                self.lunge_dir = self.enemy.dir_to(player_pos)
                self.enemy.node.clearColorScale()
                self.phase, self.t = "lunge", 0.0

        elif self.phase == "lunge":
            p = self.enemy.node.getPos()
            ahead = Vec3(p.x + self.lunge_dir.x * 5, p.y + self.lunge_dir.y * 5, p.z)
            self.enemy.move_toward(ahead, ENEMY_ATTACK_LUNGE_SPEED, dt)
            if self.t >= ENEMY_ATTACK_LUNGE_TIME:
                self.phase, self.t = "recover", 0.0

        else:  # recover
            if self.t >= ENEMY_ATTACK_COOLDOWN:
                if self.enemy.player_dist(player_pos) < ENEMY_DETECT_RANGE:
                    return "chase"
                return "search"
        return None

    def exit(self):
        self.enemy.node.clearColorScale()


class Search(State):
    """Move to the last-seen spot and look around before giving up."""
    name = "search"

    def update(self, dt, player_pos):
        self.t += dt
        if self.enemy.player_dist(player_pos) < ENEMY_DETECT_RANGE:
            return "chase"
        remaining = self.enemy.move_toward(self.enemy.last_seen, ENEMY_SPEED, dt)
        if remaining < 0.5:
            self.enemy.node.setH(self.enemy.node.getH() + 120 * dt)   # scan around
        if self.t >= ENEMY_SEARCH_TIME:
            return "return"
        return None


class Return(State):
    """Walk back to the home room, then resume patrolling."""
    name = "return"

    def update(self, dt, player_pos):
        if self.enemy.player_dist(player_pos) < ENEMY_DETECT_RANGE:
            return "chase"
        remaining = self.enemy.move_toward(self.enemy.home, ENEMY_SPEED, dt)
        if remaining < 0.5:
            return "patrol"
        return None


STATES = {cls.name: cls for cls in (Patrol, Chase, Attack, Search, Return)}
