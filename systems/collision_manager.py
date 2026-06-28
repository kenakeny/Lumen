from panda3d.core import (
    CollisionTraverser, CollisionHandlerEvent,
    CollisionHandlerPusher, CollisionHandlerQueue,
)


class CollisionManager:
    def __init__(self, app):
        self.app = app
        self.traverser = CollisionTraverser()

        # event handler for triggers (orb pickup, hazards)
        self.handler = CollisionHandlerEvent()
        self.handler.addInPattern("%fn-into-%in")

        # pusher handler for solid environment collisions
        self.pusher = CollisionHandlerPusher()

        # queue handler for ground ray
        self.ray_queue = CollisionHandlerQueue()

        # we traverse manually in the update loop for correct timing

    def register_from_collider(self, col_np):
        self.traverser.addCollider(col_np, self.handler)

    def register_pusher(self, col_np, target_np):
        self.pusher.addCollider(col_np, target_np)
        self.traverser.addCollider(col_np, self.pusher)

    def register_ray(self, ray_np):
        self.traverser.addCollider(ray_np, self.ray_queue)

    def traverse(self):
        self.traverser.traverse(self.app.render)

    def get_ground_z(self):
        if self.ray_queue.getNumEntries() == 0:
            return None
        self.ray_queue.sortEntries()
        entry = self.ray_queue.getEntry(0)
        return entry.getSurfacePoint(self.app.render).z

    def accept(self, pattern, callback):
        self.app.accept(pattern, callback)
