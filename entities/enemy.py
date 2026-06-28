import random
from math import atan2, degrees
from panda3d.core import Vec3, Vec4, CollisionSphere, CollisionNode, PointLight
from config import (
    Masks, ROOM_SIZE, ENEMY_SPEED, ENEMY_CHASE_SPEED, ENEMY_DETECT_RANGE,
)


class Enemy:
    def __init__(self, app, position, room_center):
        self.app = app
        self.alive = True
        self.room_center = room_center
        self.state = "patrol"
        self._patrol_target = None
        self._state_timer = 0.0

        self.node = app.loader.loadModel("models/frowney")
        self.node.reparentTo(app.render)
        self.node.setScale(0.6)
        self.node.setPos(position)
        self.node.setTextureOff(1)
        self.node.setColor(Vec4(1.0, 0.2, 0.2, 1.0))

        self.light = PointLight("enemy_light")
        self.light.setColor(Vec4(1.0, 0.1, 0.0, 1.0))
        self.light.setAttenuation((1, 0.3, 0.5))
        self.light_np = self.node.attachNewNode(self.light)
        app.render.setLight(self.light_np)

        col_node = CollisionNode("enemy")
        col_node.addSolid(CollisionSphere(0, 0, 0, 0.8))
        col_node.setFromCollideMask(Masks.EMPTY)
        col_node.setIntoCollideMask(Masks.ENEMY)
        self.col_np = self.node.attachNewNode(col_node)

        self._pick_patrol_target()

    def _pick_patrol_target(self):
        hs = ROOM_SIZE / 2 - 1.5
        cx, cy = self.room_center.x, self.room_center.y
        self._patrol_target = Vec3(
            cx + random.uniform(-hs, hs),
            cy + random.uniform(-hs, hs),
            self.node.getZ(),
        )

    def update(self, dt, player_pos):
        if not self.alive:
            return

        pos = self.node.getPos()
        to_player = player_pos - pos
        to_player.z = 0
        dist = to_player.length()

        if dist < ENEMY_DETECT_RANGE:
            self.state = "chase"
        else:
            self.state = "patrol"

        if self.state == "chase":
            speed = ENEMY_CHASE_SPEED
            if dist > 0.5:
                direction = to_player
                direction.normalize()
                new_pos = pos + direction * speed * dt
                new_pos.z = pos.z
                self.node.setPos(new_pos)
                self.node.setH(degrees(atan2(-direction.x, direction.y)) + 180)

        elif self.state == "patrol":
            speed = ENEMY_SPEED
            to_target = self._patrol_target - pos
            to_target.z = 0
            if to_target.length() < 0.5:
                self._pick_patrol_target()
            else:
                direction = to_target
                direction.normalize()
                new_pos = pos + direction * speed * dt
                new_pos.z = pos.z
                self.node.setPos(new_pos)
                self.node.setH(degrees(atan2(-direction.x, direction.y)) + 180)

        # bob up and down
        self._state_timer += dt
        bob = 0.3 * abs((self._state_timer % 1.0) - 0.5)
        self.node.setZ(self.room_center.z - 1 + bob)

    def destroy(self):
        self.alive = False
        self.app.render.clearLight(self.light_np)
        self.light_np.removeNode()
        self.col_np.removeNode()
        self.node.removeNode()
