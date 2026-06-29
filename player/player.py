from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpPosInterval
from panda3d.core import (
    Vec3, CollisionSphere, CollisionNode, CollisionRay, KeyboardButton,
)
from math import atan2, degrees
from config import PLAYER_SPEED, SPRINT_MULTIPLIER, GRAVITY, JUMP_SPEED, Masks


class Player:
    def __init__(self, app):
        self.app = app
        self.hp = 100
        self.speed = PLAYER_SPEED
        self.vel_z = 0.0
        self.is_grounded = True
        self.aim_dir = Vec3(0, 1, 0)   # world-space facing/shoot direction

        self.node = Actor(
            "assets/models/PandaChan/act_p3d_chan.egg.pz",
            {
                "idle": "assets/models/PandaChan/a_p3d_chan_idle.egg.pz",
                "walk": "assets/models/PandaChan/a_p3d_chan_walk.egg.pz",
                "run": "assets/models/PandaChan/a_p3d_chan_run.egg.pz",
            }
        )
        self.node.reparentTo(app.render)
        self.node.setScale(1)
        self.node.setPos(0, 0, 0)
        self.node.loop("idle")

        col_node = CollisionNode("player")
        col_node.addSolid(CollisionSphere(0, 0, 0.7, 0.7))
        col_node.setFromCollideMask(Masks.ORB | Masks.HAZARD | Masks.ENEMY)
        col_node.setIntoCollideMask(Masks.PLAYER)
        self.col_np = self.node.attachNewNode(col_node)

        push_node = CollisionNode("player_push")
        push_node.addSolid(CollisionSphere(0, 0, 0.7, 0.7))
        push_node.setFromCollideMask(Masks.WALL)
        push_node.setIntoCollideMask(Masks.EMPTY)
        self.push_np = self.node.attachNewNode(push_node)

        ray_node = CollisionNode("player_ray")
        ray_node.addSolid(CollisionRay(0, 0, 2.0, 0, 0, -1))
        ray_node.setFromCollideMask(Masks.FLOOR)
        ray_node.setIntoCollideMask(Masks.EMPTY)
        self.ray_np = self.node.attachNewNode(ray_node)

        # Poll keyboard state each frame instead of binding press/release
        # events. Event-based input drops keys when a modifier (Shift) is held
        # because Panda3D fires "shift-w" instead of "w"; polling button state
        # is modifier-agnostic, so diagonals and sprint-while-moving just work.
        self._mw = app.mouseWatcherNode
        self._buttons = {
            "forward":  KeyboardButton.ascii_key("w"),
            "backward": KeyboardButton.ascii_key("s"),
            "left":     KeyboardButton.ascii_key("a"),
            "right":    KeyboardButton.ascii_key("d"),
            "jump":     KeyboardButton.space(),
            "sprint":   KeyboardButton.shift(),
        }
        self._current_anim = "idle"

    def _down(self, action):
        return self._mw.is_button_down(self._buttons[action])

    def update(self, dt, cam_yaw=0.0):
        dt = min(dt, 0.05)

        input_dir = Vec3(0, 0, 0)
        if self._down("forward"):
            input_dir.y += 1
        if self._down("backward"):
            input_dir.y -= 1
        if self._down("left"):
            input_dir.x -= 1
        if self._down("right"):
            input_dir.x += 1

        # Single source of truth: the camera's flattened forward vector.
        # Facing, aim, and movement are all derived from it every frame, so
        # orbiting (and releasing) needs no special handling.
        fwd = self.app.cam_controller.get_forward()
        right = Vec3(fwd.y, -fwd.x, 0)
        self.aim_dir = fwd
        # PandaChan's model front is offset 180deg, so add it for the visual
        self.node.setH(degrees(atan2(-fwd.x, fwd.y)) + 180)

        moving = input_dir.lengthSquared() > 0
        if moving:
            input_dir.normalize()
            # W follows camera-forward; A/D strafe along its perpendicular
            direction = fwd * input_dir.y + right * input_dir.x
            speed = self.speed
            if self._down("sprint"):
                speed *= SPRINT_MULTIPLIER
            pos = self.node.getPos()
            pos.x += direction.x * speed * dt
            pos.y += direction.y * speed * dt
            self.node.setFluidPos(pos)

        if self._down("jump") and self.is_grounded:
            self.vel_z = JUMP_SPEED
            self.is_grounded = False

        if not self.is_grounded:
            self.vel_z -= GRAVITY * dt
            pos = self.node.getPos()
            pos.z += self.vel_z * dt
            self.node.setPos(pos)

        if moving and self._current_anim != "run":
            self.node.loop("run")
            self._current_anim = "run"
        elif not moving and self._current_anim != "idle":
            self.node.loop("idle")
            self._current_anim = "idle"

        if moving and self._down("sprint"):
            self.node.setPlayRate(1.1, "run")
        elif moving:
            self.node.setPlayRate(0.7, "run")

    def apply_ground(self, ground_z):
        pos = self.node.getPos()
        if self.is_grounded:
            pos.z = ground_z
            self.node.setPos(pos)
            self.vel_z = 0.0
        elif pos.z <= ground_z + 0.05:
            pos.z = ground_z
            self.node.setPos(pos)
            self.vel_z = 0.0
            self.is_grounded = True

    def start_falling(self):
        if self.is_grounded:
            self.is_grounded = False

    def take_damage(self, amount):
        self.hp -= amount
        self.node.setColorScale(1, 0.3, 0.3, 1)
        Sequence(Wait(0.15), Func(self.node.clearColorScale)).start()
        if self.hp <= 0:
            self.hp = 0
            self.die()

    def apply_knockback(self, direction, force=2.5):
        pos = self.node.getPos()
        target = pos + direction * force
        LerpPosInterval(self.node, 0.2, target, blendType="easeOut").start()

    def die(self):
        print("Player has died.")

    def heal(self, amount):
        self.hp += amount
        if self.hp > 100:
            self.hp = 100
