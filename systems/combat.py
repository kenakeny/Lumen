from math import sin, cos, radians
from direct.interval.IntervalGlobal import Sequence, LerpScaleInterval, LerpColorScaleInterval, Parallel, Func
from panda3d.core import Vec3, Vec4, CollisionSphere, CollisionNode
from config import (
    Masks, PROJECTILE_SPEED, PROJECTILE_LIFETIME, SHOOT_COOLDOWN,
    ENEMY_KILL_SCORE,
)


class Projectile:
    def __init__(self, app, pos, direction):
        self.app = app
        self.direction = direction
        self.age = 0.0
        self.alive = True

        self.node = app.loader.loadModel("assets/models/BambooLaser/bambooLaser.egg")
        self.node.reparentTo(app.render)
        self.node.setScale(3)
        self.node.setPos(pos)
        self.node.setColor(Vec4(0.2, 0.9, 1.0, 1.0))
        self.node.setBillboardAxis()

        col_node = CollisionNode("projectile")
        col_node.addSolid(CollisionSphere(0, 0, 0, 0.3))
        col_node.setFromCollideMask(Masks.ENEMY)
        col_node.setIntoCollideMask(Masks.EMPTY)
        self.col_np = self.node.attachNewNode(col_node)

    def update(self, dt):
        if not self.alive:
            return False
        self.age += dt
        if self.age >= PROJECTILE_LIFETIME:
            return False
        self.node.setPos(self.node.getPos() + self.direction * PROJECTILE_SPEED * dt)
        return True

    def destroy(self):
        self.alive = False
        self.col_np.removeNode()
        self.node.removeNode()


class CombatSystem:
    def __init__(self, app):
        self.app = app
        self.projectiles = []
        self.shoot_cooldown = 0.0
        app.accept("mouse1", self._shoot)

    def _shoot(self):
        if self.shoot_cooldown > 0:
            return
        player = self.app.player
        heading = player.node.getH()
        rad = radians(heading)
        direction = Vec3(-sin(rad), cos(rad), 0)
        spawn_pos = player.node.getPos() + Vec3(0, 0, 1) + direction * 1.0

        proj = Projectile(self.app, spawn_pos, direction)
        self.app.collision_mgr.register_from_collider(proj.col_np)
        self.projectiles.append(proj)
        self.shoot_cooldown = SHOOT_COOLDOWN

    def update(self, dt):
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        alive = []
        for p in self.projectiles:
            if p.update(dt):
                alive.append(p)
            else:
                p.destroy()
        self.projectiles = alive

    def on_hit(self, entry):
        proj_np = entry.getFromNodePath().getParent()
        enemy_np = entry.getIntoNodePath().getParent()

        for p in self.projectiles:
            if p.alive and p.node == proj_np:
                hit_pos = p.node.getPos()
                p.destroy()
                self.projectiles.remove(p)
                self._spawn_hit_effect(hit_pos)
                break

        for enemy in self.app.enemies:
            if enemy.alive and enemy.node == enemy_np:
                enemy.destroy()
                self.app.score += ENEMY_KILL_SCORE
                self.app.hud.show_feedback(
                    f"+{ENEMY_KILL_SCORE} Kill!",
                    color=(1, 0.5, 0.1, 1),
                )
                break

    def _spawn_hit_effect(self, pos):
        effect = self.app.loader.loadModel("assets/models/BambooLaser/bambooLaserHit.egg")
        effect.reparentTo(self.app.render)
        effect.setPos(pos)
        effect.setScale(0.5)
        effect.setBillboardPointEye()
        effect.setColor(Vec4(0.3, 1.0, 1.0, 1.0))
        Sequence(
            Parallel(
                LerpScaleInterval(effect, 0.3, 3.0, startScale=0.5),
                LerpColorScaleInterval(effect, 0.3, (1, 1, 1, 0)),
            ),
            Func(effect.removeNode),
        ).start()

    def destroy_all(self):
        for p in self.projectiles:
            p.destroy()
        self.projectiles.clear()
