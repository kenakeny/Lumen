import random
from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d
from player.player import Player
from player.camera_controller import CameraController
from entities.orb import Orb
from systems.collision_manager import CollisionManager
from world.dungeon import Dungeon
from config import ORB_SCORE_VALUE


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
        self.orbs = []
        room_centers = self.dungeon.get_room_centers()
        orb_rooms = random.sample(room_centers, min(5, len(room_centers)))
        for pos in orb_rooms:
            self.orbs.append(Orb(self, pos))

        self.collision_mgr.accept("player-into-orb", self._on_orb_collected)

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

    def _update(self, task):
        dt = globalClock.getDt()
        self.player.update(dt, self.cam_controller.yaw)

        # traverse collisions after movement so ground ray is current
        self.collision_mgr.traverse()

        ground_z = self.collision_mgr.get_ground_z()
        if ground_z is not None:
            self.player.apply_ground(ground_z)
        else:
            self.player.start_falling()

        self.cam_controller.update(dt)
        return task.cont
