from direct.actor.Actor import Actor
from panda3d.core import Vec3, CollisionSphere, CollisionNode, CollisionRay
from math import atan2, degrees, sin, cos, radians
from config import PLAYER_SPEED, GRAVITY, JUMP_SPEED, Masks


class Player:
    def __init__(self, app):
        self.app = app
        self.hp = 100
        self.speed = PLAYER_SPEED
        self.vel_z = 0.0
        self.is_grounded = True

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

        # trigger collision (orbs, hazards, enemies)
        col_node = CollisionNode("player")
        col_node.addSolid(CollisionSphere(0, 0, 0.7, 0.7))
        col_node.setFromCollideMask(Masks.ORB | Masks.HAZARD | Masks.ENEMY)
        col_node.setIntoCollideMask(Masks.PLAYER)
        self.col_np = self.node.attachNewNode(col_node)

        # wall pusher sphere (only walls push the player, not floors)
        push_node = CollisionNode("player_push")
        push_node.addSolid(CollisionSphere(0, 0, 0.7, 0.7))
        push_node.setFromCollideMask(Masks.WALL)
        push_node.setIntoCollideMask(Masks.EMPTY)
        self.push_np = self.node.attachNewNode(push_node)

        # ground ray (cast downward to detect floor height)
        ray_node = CollisionNode("player_ray")
        ray_node.addSolid(CollisionRay(0, 0, 2.0, 0, 0, -1))
        ray_node.setFromCollideMask(Masks.FLOOR)
        ray_node.setIntoCollideMask(Masks.EMPTY)
        self.ray_np = self.node.attachNewNode(ray_node)

        self.key_map = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "jump": False,
        }
        self._current_anim = "idle"
        self._setup_input()

    def _setup_input(self):
        self.app.accept("w", self._set_key, ["forward", True])
        self.app.accept("w-up", self._set_key, ["forward", False])
        self.app.accept("s", self._set_key, ["backward", True])
        self.app.accept("s-up", self._set_key, ["backward", False])
        self.app.accept("a", self._set_key, ["left", True])
        self.app.accept("a-up", self._set_key, ["left", False])
        self.app.accept("d", self._set_key, ["right", True])
        self.app.accept("d-up", self._set_key, ["right", False])
        self.app.accept("space", self._set_key, ["jump", True])
        self.app.accept("space-up", self._set_key, ["jump", False])

    def _set_key(self, key, value):
        self.key_map[key] = value

    def update(self, dt, cam_yaw=0.0):
        dt = min(dt, 0.05)

        input_dir = Vec3(0, 0, 0)
        if self.key_map["forward"]:
            input_dir.y += 1
        if self.key_map["backward"]:
            input_dir.y -= 1
        if self.key_map["left"]:
            input_dir.x -= 1
        if self.key_map["right"]:
            input_dir.x += 1

        moving = input_dir.lengthSquared() > 0
        if moving:
            input_dir.normalize()
            rad = radians(cam_yaw)
            direction = Vec3(
                input_dir.x * cos(rad) - input_dir.y * sin(rad),
                input_dir.x * sin(rad) + input_dir.y * cos(rad),
                0,
            )
            pos = self.node.getPos()
            pos.x += direction.x * self.speed * dt
            pos.y += direction.y * self.speed * dt
            self.node.setPos(pos)
            angle = degrees(atan2(-direction.x, direction.y)) + 180
            self.node.setH(angle)

        # jumping
        if self.key_map["jump"] and self.is_grounded:
            self.vel_z = JUMP_SPEED
            self.is_grounded = False

        # gravity (only when airborne)
        if not self.is_grounded:
            self.vel_z -= GRAVITY * dt
            pos = self.node.getPos()
            pos.z += self.vel_z * dt
            self.node.setPos(pos)

        # animation
        if moving and self._current_anim != "run":
            self.node.loop("run")
            self._current_anim = "run"
        elif not moving and self._current_anim != "idle":
            self.node.loop("idle")
            self._current_anim = "idle"

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
        if self.hp <= 0:
            self.hp = 0
            self.die()

    def die(self):
        print("Player has died.")

    def heal(self, amount):
        self.hp += amount
        if self.hp > 100:
            self.hp = 100
