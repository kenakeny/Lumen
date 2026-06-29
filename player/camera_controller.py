from panda3d.core import (
    Vec3, Point3, NodePath, WindowProperties,
    CollisionTraverser, CollisionSegment, CollisionNode, CollisionHandlerQueue,
)
from math import sin, cos, radians
from config import (
    CAM_DISTANCE, CAM_HEIGHT, CAM_ELEV, CAM_ELEV_MIN, CAM_ELEV_MAX,
    CAM_SENSITIVITY, CAM_DAMPING, Masks,
)


class CameraController:
    def __init__(self, app, target_node):
        self.app = app
        self.target = target_node
        self.distance = CAM_DISTANCE
        self.height = CAM_HEIGHT
        self.damping = CAM_DAMPING

        self.yaw = 0.0
        self.elev = CAM_ELEV          # view elevation: negative looks down, positive up
        self.elev_min = CAM_ELEV_MIN
        self.elev_max = CAM_ELEV_MAX
        self.mouse_sens = CAM_SENSITIVITY

        self.zoom_min = 5.0
        self.zoom_max = 40.0
        self.zoom_step = 2.0

        self._look_ready = False

        # hide the OS cursor; the HUD crosshair is the aim marker now
        props = WindowProperties()
        props.setCursorHidden(True)
        app.win.requestProperties(props)

        self._dummy = NodePath("cam_dummy")
        self._dummy.reparentTo(app.render)

        # segment from the player to the camera, used to pull the camera in
        # front of any wall that would otherwise block the view
        seg_node = CollisionNode("cam_seg")
        self._cam_seg = CollisionSegment(0, 0, 0, 0, 0, 1)
        seg_node.addSolid(self._cam_seg)
        seg_node.setFromCollideMask(Masks.WALL)
        seg_node.setIntoCollideMask(Masks.EMPTY)
        self._cam_seg_np = app.render.attachNewNode(seg_node)
        self._cam_trav = CollisionTraverser("cam_trav")
        self._cam_queue = CollisionHandlerQueue()
        self._cam_trav.addCollider(self._cam_seg_np, self._cam_queue)

        # Mouse-look: moving the mouse steers the camera (and therefore aim,
        # since aim = camera-forward). Wheel zooms.
        app.accept("wheel_up", self._zoom_in)
        app.accept("wheel_down", self._zoom_out)

    def get_forward(self):
        """Camera forward flattened to the ground plane, normalized.

        The single source of truth for facing/aim/movement. It depends only on
        the orbit yaw (pitch cancels when flattened to XY), so it stays correct
        during a right-drag orbit and after release with no special-casing, and
        avoids the jitter you'd get from reading the smoothed camera transform.
        """
        rad = radians(self.yaw)
        return Vec3(sin(rad), cos(rad), 0)

    def get_aim_dir(self):
        """Full 3D direction the crosshair (screen center) points, built
        directly from yaw + elevation. The camera is oriented along this, so
        bullets fired down it go exactly where the crosshair is, up or down."""
        yaw_rad, e = radians(self.yaw), radians(self.elev)
        return Vec3(
            sin(yaw_rad) * cos(e),
            cos(yaw_rad) * cos(e),
            sin(e),
        )

    def _zoom_in(self):
        self.distance = max(self.zoom_min, self.distance - self.zoom_step)

    def _zoom_out(self):
        self.distance = min(self.zoom_max, self.distance + self.zoom_step)

    def _mouselook(self):
        """Rotate the camera from raw mouse motion, recentering the pointer
        each frame so it never hits the window edge (FPS-style mouse-look)."""
        win = self.app.win
        cx, cy = win.getXSize() // 2, win.getYSize() // 2
        ptr = win.getPointer(0)
        x, y = ptr.getX(), ptr.getY()
        if not win.movePointer(0, cx, cy):
            return                       # pointer outside window; skip this frame
        if not self._look_ready:
            self._look_ready = True      # first frame just centers, no jump
            return
        self.yaw += (x - cx) * self.mouse_sens
        # mouse up (y < center) raises the view; clamp to the aim range
        self.elev = max(
            self.elev_min,
            min(self.elev_max, self.elev + (cy - y) * self.mouse_sens),
        )

    def _wall_occlusion(self, look_target, desired_pos):
        """If a wall sits between the player and the desired camera spot,
        return a point just in front of that wall; otherwise None."""
        self._cam_seg.setPointA(look_target)
        self._cam_seg.setPointB(desired_pos)
        self._cam_trav.traverse(self.app.render)
        if self._cam_queue.getNumEntries() == 0:
            return None
        self._cam_queue.sortEntries()
        hit = self._cam_queue.getEntry(0).getSurfacePoint(self.app.render)
        to_hit = hit - look_target
        d = to_hit.length()
        if d < 0.01:
            return None
        to_hit *= max(d - 0.4, 0.5) / d   # back off a little from the wall
        return Point3(look_target + to_hit)

    def update(self, dt):
        self._mouselook()

        target_pos = self.target.getPos()
        look_target = target_pos + Vec3(0, 0, self.height)

        # camera sits behind the player along the aim line and looks straight
        # down it, so screen-center == aim direction at any elevation
        forward = self.get_aim_dir()
        desired_pos = Point3(look_target - forward * self.distance)
        if desired_pos.z < 0.5:          # don't sink under the floor when aiming up
            desired_pos.z = 0.5

        occ_pos = self._wall_occlusion(look_target, desired_pos)
        occluded = occ_pos is not None
        if occluded:
            desired_pos = occ_pos

        self._dummy.setPos(desired_pos)
        self._dummy.lookAt(desired_pos + forward)
        desired_quat = self._dummy.getQuat(self.app.render)

        current_pos = self.app.camera.getPos()
        current_quat = self.app.camera.getQuat(self.app.render)

        t = min(1.0, self.damping * dt)

        dot = current_quat.dot(desired_quat)
        if dot < 0:
            desired_quat = -desired_quat
        new_quat = current_quat * ((current_quat.conjugate() * desired_quat) ** t)
        new_quat.normalize()

        # snap straight to the clamped spot when a wall is in the way so the
        # view never slips behind it; smooth-follow otherwise
        if occluded:
            new_pos = desired_pos
        else:
            new_pos = current_pos + (desired_pos - current_pos) * t

        self.app.camera.setPos(new_pos)
        self.app.camera.setQuat(self.app.render, new_quat)
