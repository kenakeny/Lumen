import random
from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d
from player.player import Player
from player.camera_controller import CameraController
from entities.orb import Orb
from entities.enemy import Enemy
from entities.hazard import HazardZone
from systems.collision_manager import CollisionManager
from world.dungeon import Dungeon
from config import (
    ORB_SCORE_VALUE, ENEMY_DAMAGE, ENEMY_DAMAGE_COOLDOWN,
    HAZARD_DAMAGE_PER_SEC,
)


class App(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        props = p3d.WindowProperties()
        props.setTitle("Lumen")
        props.setSize(1024, 720)
        self.win.requestProperties(props)

        self._setup_lighting()

        self.dungeon = Dungeon(self)

        self.collision_mgr = CollisionManager(self)
        self.player = Player(self)
        self.player.node.setPos(self.dungeon.get_spawn_pos())
        self.collision_mgr.register_from_collider(self.player.col_np)
        self.collision_mgr.register_pusher(self.player.push_np, self.player.node)
        self.collision_mgr.register_ray(self.player.ray_np)

        self.cam_controller = CameraController(self, self.player.node)

        self.score = 0
        self._enemy_dmg_cooldown = 0.0
        self._in_hazard = False
        self._hazard_timer = 0.0

        room_centers = self.dungeon.get_room_centers()
        spawn_room = self.dungeon.get_spawn_pos()

        non_spawn = [c for c in room_centers
                     if abs(c.x - spawn_room.x) > 1 or abs(c.y - spawn_room.y) > 1]

        # orbs
        self.orbs = []
        orb_rooms = random.sample(non_spawn, min(5, len(non_spawn)))
        for pos in orb_rooms:
            self.orbs.append(Orb(self, pos))

        # enemies — one per ~third of rooms, not in spawn room
        self.enemies = []
        enemy_count = max(1, len(non_spawn) // 3)
        enemy_rooms = random.sample(non_spawn, min(enemy_count, len(non_spawn)))
        for center in enemy_rooms:
            self.enemies.append(Enemy(self, center, center))

        # hazards — a few rooms get hazard zones
        self.hazards = []
        remaining = [c for c in non_spawn if c not in enemy_rooms]
        hazard_count = max(1, len(remaining) // 4)
        hazard_rooms = random.sample(remaining, min(hazard_count, len(remaining)))
        for center in hazard_rooms:
            self.hazards.append(HazardZone(self, center))

        # collision events
        self.collision_mgr.accept("player-into-orb", self._on_orb_collected)
        self.collision_mgr.accept("player-into-enemy", self._on_enemy_hit)
        self.collision_mgr.accept("player-into-hazard", self._on_hazard_enter)

        self.taskMgr.add(self._update, "game_update")

    def _setup_lighting(self):
        ambient = p3d.AmbientLight("ambient")
        ambient.setColor((0.3, 0.3, 0.3, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        sun = p3d.DirectionalLight("sun")
        sun.setColor((1, 1, 1, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(45, -45, 0)
        self.render.setLight(sun_np)

    def _on_orb_collected(self, entry):
        orb_np = entry.getIntoNodePath().getParent()
        for orb in self.orbs:
            if not orb.collected and orb.node == orb_np:
                orb.destroy()
                self.score += ORB_SCORE_VALUE
                print(f"Score: {self.score}")
                break

    def _on_enemy_hit(self, entry):
        if self._enemy_dmg_cooldown > 0:
            return
        self.player.take_damage(ENEMY_DAMAGE)
        self._enemy_dmg_cooldown = ENEMY_DAMAGE_COOLDOWN
        print(f"Hit by enemy! HP: {self.player.hp}")

    def _on_hazard_enter(self, entry):
        self._in_hazard = True
        self._hazard_timer = 0.0

    def _update(self, task):
        dt = globalClock.getDt()

        self.player.update(dt, self.cam_controller.yaw)

        player_pos = self.player.node.getPos()
        for enemy in self.enemies:
            enemy.update(dt, player_pos)

        # traverse collisions after movement so ground ray is current
        self.collision_mgr.traverse()

        ground_z = self.collision_mgr.get_ground_z()
        if ground_z is not None:
            self.player.apply_ground(ground_z)
        else:
            self.player.start_falling()

        # enemy damage cooldown
        if self._enemy_dmg_cooldown > 0:
            self._enemy_dmg_cooldown -= dt

        # hazard continuous damage
        if self._in_hazard:
            self._hazard_timer += dt
            if self._hazard_timer >= 0.5:
                self.player.take_damage(int(HAZARD_DAMAGE_PER_SEC * self._hazard_timer))
                self._hazard_timer = 0.0
                print(f"Hazard damage! HP: {self.player.hp}")
            # reset each frame — re-set by collision event if still overlapping
            self._in_hazard = False

        self.cam_controller.update(dt)
        return task.cont
