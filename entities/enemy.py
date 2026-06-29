import random
from math import atan2, degrees
from panda3d.core import Vec3, Vec4, CollisionSphere, CollisionNode, PointLight
from config import Masks, ROOM_SIZE
from entities.enemy_states import STATES


class Enemy:
    def __init__(self, app, position, room_center):
        self.app = app
        self.alive = True
        self.home = room_center
        self.patrol_target = Vec3(position)
        self.last_seen = Vec3(position)
        self._bob_timer = 0.0

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

        self.state = None
        self.state_name = None
        self.set_state("patrol")

    # --- FSM ----------------------------------------------------------------

    def set_state(self, name):
        if self.state is not None:
            self.state.exit()
        self.state = STATES[name](self)
        self.state_name = name
        self.state.enter()

    def update(self, dt, player_pos):
        if not self.alive:
            return

        nxt = self.state.update(dt, player_pos)
        if nxt is not None and nxt != self.state_name:
            self.set_state(nxt)

        # bob up and down (purely visual)
        self._bob_timer += dt
        bob = 0.3 * abs((self._bob_timer % 1.0) - 0.5)
        self.node.setZ(self.home.z - 1 + bob)

    # --- helpers the states use --------------------------------------------

    def player_dist(self, player_pos):
        p = self.node.getPos()
        return Vec3(player_pos.x - p.x, player_pos.y - p.y, 0).length()

    def dir_to(self, point):
        p = self.node.getPos()
        d = Vec3(point.x - p.x, point.y - p.y, 0)
        if d.lengthSquared() > 1e-6:
            d.normalize()
        return d

    def face(self, point):
        d = self.dir_to(point)
        if d.lengthSquared() > 1e-6:
            self.node.setH(degrees(atan2(-d.x, d.y)) + 180)

    def move_toward(self, target, speed, dt):
        """Step toward ``target`` (XY only) and face it. Returns the distance
        that remained *before* this step, so states can detect arrival."""
        pos = self.node.getPos()
        d = Vec3(target.x - pos.x, target.y - pos.y, 0)
        remaining = d.length()
        if remaining > 1e-4:
            d /= remaining
            step = min(speed * dt, remaining)
            self.node.setPos(pos.x + d.x * step, pos.y + d.y * step, pos.z)
            self.node.setH(degrees(atan2(-d.x, d.y)) + 180)
        return remaining

    def remember(self, player_pos):
        self.last_seen = Vec3(player_pos.x, player_pos.y, self.node.getZ())

    def pick_patrol_target(self):
        hs = ROOM_SIZE / 2 - 1.5
        self.patrol_target = Vec3(
            self.home.x + random.uniform(-hs, hs),
            self.home.y + random.uniform(-hs, hs),
            self.node.getZ(),
        )

    def destroy(self):
        self.alive = False
        self.app.render.clearLight(self.light_np)
        self.light_np.removeNode()
        self.col_np.removeNode()
        self.node.removeNode()
