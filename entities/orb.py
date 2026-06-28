from panda3d.core import Vec3, Vec4, PointLight, CollisionSphere, CollisionNode
from config import Masks


class Orb:
    def __init__(self, app, position):
        self.app = app
        self.collected = False

        self.node = app.loader.loadModel("models/smiley")
        self.node.reparentTo(app.render)
        self.node.setScale(0.4)
        self.node.setPos(position)
        self.node.setTextureOff(1)
        self.node.setColor(Vec4(0.2, 0.8, 1.0, 1.0))

        self.light = PointLight("orb_light")
        self.light.setColor(Vec4(0.2, 0.6, 1.0, 1.0))
        self.light.setAttenuation((1, 0, 0.5))
        self.light_np = self.node.attachNewNode(self.light)
        app.render.setLight(self.light_np)

        self.node.hprInterval(2.0, Vec3(360, 0, 0)).loop()

        # collision
        col_node = CollisionNode("orb")
        col_node.addSolid(CollisionSphere(0, 0, 0, 1))
        col_node.setFromCollideMask(Masks.EMPTY)
        col_node.setIntoCollideMask(Masks.ORB)
        self.col_np = self.node.attachNewNode(col_node)

    def destroy(self):
        self.collected = True
        self.app.render.clearLight(self.light_np)
        self.light_np.removeNode()
        self.col_np.removeNode()
        self.node.removeNode()
