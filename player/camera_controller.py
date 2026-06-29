from panda3d.core import Vec3, Point3, NodePath
from math import sin, cos, radians
from config import CAM_DISTANCE, CAM_HEIGHT, CAM_PITCH, CAM_DAMPING


class CameraController:
    def __init__(self, app, target_node):
        self.app = app
        self.target = target_node
        self.distance = CAM_DISTANCE
        self.height = CAM_HEIGHT
        self.damping = CAM_DAMPING

        self.yaw = 0.0
        self.pitch = CAM_PITCH
        self.pitch_min = 5.0
        self.pitch_max = 70.0
        self.mouse_sens = 200.0

        self.zoom_min = 5.0
        self.zoom_max = 40.0
        self.zoom_step = 2.0

        self._rotating = False
        self._last_mouse = None

        self._dummy = NodePath("cam_dummy")
        self._dummy.reparentTo(app.render)

        app.accept("wheel_up", self._zoom_in)
        app.accept("wheel_down", self._zoom_out)
        app.accept("mouse3", self._start_rotate)
        app.accept("mouse3-up", self._stop_rotate)

    def _zoom_in(self):
        self.distance = max(self.zoom_min, self.distance - self.zoom_step)

    def _zoom_out(self):
        self.distance = min(self.zoom_max, self.distance + self.zoom_step)

    def _start_rotate(self):
        self._rotating = True
        self._last_mouse = None

    def _stop_rotate(self):
        self._rotating = False
        self._last_mouse = None

    def _update_rotation(self):
        if not self._rotating:
            return
        if not self.app.mouseWatcherNode.hasMouse():
            return

        mx = self.app.mouseWatcherNode.getMouseX()
        my = self.app.mouseWatcherNode.getMouseY()

        if self._last_mouse is not None:
            dx = mx - self._last_mouse[0]
            dy = my - self._last_mouse[1]
            self.yaw -= dx * self.mouse_sens
            self.pitch = max(self.pitch_min, min(self.pitch_max, self.pitch + dy * self.mouse_sens))

        self._last_mouse = (mx, my)

    def update(self, dt):
        self._update_rotation()

        target_pos = self.target.getPos()

        yaw_rad = radians(self.yaw)
        pitch_rad = radians(self.pitch)
        desired_pos = Point3(
            target_pos.x - self.distance * sin(yaw_rad) * cos(pitch_rad),
            target_pos.y - self.distance * cos(yaw_rad) * cos(pitch_rad),
            target_pos.z + self.distance * sin(pitch_rad),
        )

        look_target = target_pos + Vec3(0, 0, self.height)
        self._dummy.setPos(desired_pos)
        self._dummy.lookAt(look_target)
        desired_quat = self._dummy.getQuat(self.app.render)

        current_pos = self.app.camera.getPos()
        current_quat = self.app.camera.getQuat(self.app.render)

        t = min(1.0, self.damping * dt)

        dot = current_quat.dot(desired_quat)
        if dot < 0:
            desired_quat = -desired_quat
        new_quat = current_quat * ((current_quat.conjugate() * desired_quat) ** t)
        new_quat.normalize()

        new_pos = current_pos + (desired_pos - current_pos) * t

        self.app.camera.setPos(new_pos)
        self.app.camera.setQuat(self.app.render, new_quat)
