from panda3d.core import Vec3, Vec4, CollisionBox, CollisionNode, Point3, PointLight
from config import Masks, ROOM_SIZE


HAZARD_SIZE = 2.5


class HazardZone:
    def __init__(self, app, position):
        self.app = app
        self.active = True
        hs = HAZARD_SIZE

        from world.room_builder import _make_box_geom, _make_material
        geom = _make_box_geom("hazard", hs, hs, 0.02)
        self.node = app.render.attachNewNode(geom)
        self.node.setPos(position.x, position.y, 0.02)

        mat = _make_material((0.6, 0.15, 0.0))
        self.node.setMaterial(mat)
        self.node.setTransparency(1)
        self.node.setColor(Vec4(0.8, 0.2, 0.0, 0.7))

        self.light = PointLight("hazard_light")
        self.light.setColor(Vec4(1.0, 0.3, 0.0, 1.0))
        self.light.setAttenuation((1, 0.5, 0.5))
        self.light_np = self.node.attachNewNode(self.light)
        self.light_np.setZ(0.5)
        app.render.setLight(self.light_np)

        col_node = CollisionNode("hazard")
        col_node.addSolid(CollisionBox(Point3(0, 0, 0.5), hs, hs, 0.5))
        col_node.setFromCollideMask(Masks.EMPTY)
        col_node.setIntoCollideMask(Masks.HAZARD)
        self.col_np = self.node.attachNewNode(col_node)

    def destroy(self):
        self.active = False
        self.app.render.clearLight(self.light_np)
        self.light_np.removeNode()
        self.col_np.removeNode()
        self.node.removeNode()
