import random
from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d
from player.player import Player
from player.camera_controller import CameraController
from entities.orb import Orb
from entities.enemy import Enemy
from entities.hazard import HazardZone, HAZARD_SIZE
from systems.collision_manager import CollisionManager
from systems.combat import CombatSystem
from systems.audio import AudioManager
from ui.hud import HUD
from ui.menu import MainMenu, PauseMenu
from world.dungeon import Dungeon
from config import (
    ORB_SCORE_VALUE, ENEMY_DAMAGE, ENEMY_DAMAGE_COOLDOWN,
    HAZARD_DAMAGE_PER_SEC, ROOM_SIZE,
    ORB_INITIAL_COUNT, ORB_MAX, ORB_SPAWN_INTERVAL,
    ENEMY_INITIAL_COUNT, ENEMY_MAX, ENEMY_SPAWN_INTERVAL,
    SPAWN_MARGIN, ENEMY_SPAWN_SAFE_DIST,
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

        # audio is persistent across games; ambient loop plays under the menu too
        self.audio = AudioManager(self)
        self.audio.start_music()

        # show the menu first; the game world and loop start on "Start"
        self._started = False
        self.menu = MainMenu(self, on_start=self._start_game)

    def _start_game(self):
        if self._started:
            return
        self._started = True
        self.paused = False
        self.pause_menu = None

        self.collision_mgr = CollisionManager(self)
        self.score = 0
        self.current_level = 1
        self._enemy_dmg_cooldown = 0.0
        self._hazard_timer = 0.0

        self._setup_world()

        self.hud = HUD(self)
        self.combat = CombatSystem(self)

        self.collision_mgr.accept("player-into-orb", self._on_orb_collected)
        self.collision_mgr.accept("player-into-enemy", self._on_enemy_hit)
        self.collision_mgr.accept("projectile-into-enemy", self.combat.on_hit)
        self.accept("escape", self._toggle_pause)

        self.taskMgr.add(self._update, "game_update")

    # --- pause / teardown / game over --------------------------------------

    def _toggle_pause(self):
        if not self._started:
            return
        if self.paused:
            self._resume()
        else:
            self._pause()

    def _pause(self):
        self.paused = True
        self.cam_controller.set_captured(False)   # free the cursor for the menu
        self.pause_menu = PauseMenu(
            self, on_resume=self._resume, on_quit=self._quit_to_menu)

    def _resume(self):
        if self.pause_menu:
            self.pause_menu.destroy()
            self.pause_menu = None
        self.paused = False
        self.cam_controller.set_captured(True)

    def _quit_to_menu(self):
        self._teardown_game()
        self.menu = MainMenu(self, on_start=self._start_game)

    def _game_over(self):
        score = self.score
        self._teardown_game()
        self.menu = MainMenu(
            self, on_start=self._start_game, message=f"You died    Score: {score}")

    def _teardown_game(self):
        self.taskMgr.remove("game_update")
        self.ignore("player-into-orb")
        self.ignore("player-into-enemy")
        self.ignore("projectile-into-enemy")
        self.ignore("escape")

        if self.pause_menu:
            self.pause_menu.destroy()
            self.pause_menu = None
        self.paused = False

        for o in self.orbs:
            if not o.collected:
                o.destroy()
        for e in self.enemies:
            if e.alive:
                e.destroy()
        for h in self.hazards:
            if h.active:
                h.destroy()
        self.orbs.clear()
        self.enemies.clear()
        self.hazards.clear()

        self.combat.destroy()
        self.cam_controller.destroy()   # also releases the mouse
        self.player.destroy()
        self.dungeon.destroy()
        self.hud.destroy()
        self._started = False

    def _setup_lighting(self):
        ambient = p3d.AmbientLight("ambient")
        ambient.setColor((0.3, 0.3, 0.3, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        sun = p3d.DirectionalLight("sun")
        sun.setColor((1, 1, 1, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(45, -45, 0)
        self.render.setLight(sun_np)

    def _setup_world(self):
        self.dungeon = Dungeon(self)

        self.player = Player(self)
        self.player.node.setPos(self.dungeon.get_spawn_pos())
        self.collision_mgr.register_from_collider(self.player.col_np)
        self.collision_mgr.register_pusher(self.player.push_np, self.player.node)
        self.collision_mgr.register_ray(self.player.ray_np)

        self.cam_controller = CameraController(self, self.player.node)

        room_centers = self.dungeon.get_room_centers()
        spawn_room = self.dungeon.get_spawn_pos()
        self.non_spawn = [c for c in room_centers
                          if abs(c.x - spawn_room.x) > 1 or abs(c.y - spawn_room.y) > 1]

        self.orbs = []
        for _ in range(ORB_INITIAL_COUNT):
            self._spawn_orb()

        self.enemies = []
        for _ in range(ENEMY_INITIAL_COUNT):
            center = random.choice(self.non_spawn)
            self.enemies.append(Enemy(self, self._scatter_in_room(center), center))

        self.hazards = []
        hazard_count = max(1, len(self.non_spawn) // 4)
        for center in random.sample(self.non_spawn, min(hazard_count, len(self.non_spawn))):
            self.hazards.append(HazardZone(self, center))

        self._orb_spawn_timer = 0.0
        self._enemy_spawn_timer = 0.0

    def _scatter_in_room(self, center):
        """Random point inside a room, kept away from the walls."""
        hs = ROOM_SIZE / 2 - SPAWN_MARGIN
        return p3d.Point3(
            center.x + random.uniform(-hs, hs),
            center.y + random.uniform(-hs, hs),
            center.z,
        )

    def _spawn_orb(self):
        center = random.choice(self.non_spawn)
        self.orbs.append(Orb(self, self._scatter_in_room(center)))

    def _spawn_enemy(self):
        # prefer rooms that aren't right on top of the player
        player_pos = self.player.node.getPos()
        far = [c for c in self.non_spawn
               if (c - player_pos).lengthSquared() > ENEMY_SPAWN_SAFE_DIST ** 2]
        center = random.choice(far or self.non_spawn)
        self.enemies.append(Enemy(self, self._scatter_in_room(center), center))

    def _update_spawns(self, dt):
        # drop dead/collected entries so the lists don't grow unbounded
        self.enemies = [e for e in self.enemies if e.alive]
        self.orbs = [o for o in self.orbs if not o.collected]

        self._orb_spawn_timer += dt
        if self._orb_spawn_timer >= ORB_SPAWN_INTERVAL:
            self._orb_spawn_timer = 0.0
            if len(self.orbs) < ORB_MAX:
                self._spawn_orb()

        self._enemy_spawn_timer += dt
        if self._enemy_spawn_timer >= ENEMY_SPAWN_INTERVAL:
            self._enemy_spawn_timer = 0.0
            if len(self.enemies) < ENEMY_MAX:
                self._spawn_enemy()

    def _on_orb_collected(self, entry):
        orb_np = entry.getIntoNodePath().getParent()
        for orb in self.orbs:
            if not orb.collected and orb.node == orb_np:
                orb.destroy()
                self.score += ORB_SCORE_VALUE
                self.audio.play("orb_pickup")
                self.hud.show_feedback(
                    f"+{ORB_SCORE_VALUE}!",
                    color=(0.2, 0.8, 1.0, 1),
                )
                break

    def _on_enemy_hit(self, entry):
        if self._enemy_dmg_cooldown > 0:
            return
        self.player.take_damage(ENEMY_DAMAGE)
        self._enemy_dmg_cooldown = ENEMY_DAMAGE_COOLDOWN
        self.audio.play("ouch")
        self.hud.show_feedback("Ouch!", color=(1, 0.2, 0.2, 1))

        enemy_pos = entry.getIntoNodePath().getParent().getPos()
        player_pos = self.player.node.getPos()
        knockback = player_pos - enemy_pos
        knockback.z = 0
        if knockback.lengthSquared() > 0:
            knockback.normalize()
        else:
            knockback = p3d.Vec3(0, 1, 0)
        self.player.apply_knockback(knockback)

    def _player_in_hazard(self):
        p = self.player.node.getPos()
        for h in self.hazards:
            if not h.active:
                continue
            hp = h.node.getPos()
            if abs(p.x - hp.x) <= HAZARD_SIZE and abs(p.y - hp.y) <= HAZARD_SIZE:
                return True
        return False

    def _update(self, task):
        if self.paused:
            return task.cont

        dt = globalClock.getDt()

        self.player.update(dt, self.cam_controller.yaw)

        player_pos = self.player.node.getPos()
        for enemy in self.enemies:
            enemy.update(dt, player_pos)

        self.combat.update(dt)
        self._update_spawns(dt)

        self.collision_mgr.traverse()

        ground_z = self.collision_mgr.get_ground_z()
        if ground_z is not None:
            self.player.apply_ground(ground_z)
        else:
            self.player.start_falling()

        if self._enemy_dmg_cooldown > 0:
            self._enemy_dmg_cooldown -= dt

        if self._player_in_hazard():
            self._hazard_timer += dt
            if self._hazard_timer >= 0.5:
                self.player.take_damage(int(HAZARD_DAMAGE_PER_SEC * self._hazard_timer))
                self._hazard_timer = 0.0
                self.hud.show_feedback("Burning!", color=(1, 0.4, 0.0, 1))
        else:
            self._hazard_timer = 0.0

        if self.player.hp <= 0:
            self._game_over()
            return task.done

        self.hud.update(self.player.hp, 100, self.score, self.current_level)
        self.cam_controller.update(dt)
        return task.cont
