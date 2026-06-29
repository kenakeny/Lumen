from direct.gui.DirectGui import DirectFrame, DirectButton
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode


class MainMenu:
    """Title screen shown before the game starts. Calls ``on_start`` when the
    player clicks Start, after tearing itself down."""

    def __init__(self, app, on_start, message=None):
        self.app = app
        self.on_start = on_start

        # dim full-screen backdrop (over-sized so it covers any aspect ratio)
        self.frame = DirectFrame(
            parent=app.aspect2d,
            frameColor=(0.04, 0.05, 0.08, 0.92),
            frameSize=(-2.0, 2.0, -1.0, 1.0),
        )

        # optional banner, e.g. shown on returning here after death
        if message:
            OnscreenText(
                parent=self.frame, text=message, pos=(0, 0.68), scale=0.07,
                fg=(1.0, 0.55, 0.45, 1), align=TextNode.ACenter,
            )

        self.title = OnscreenText(
            parent=self.frame, text="LUMEN", pos=(0, 0.45), scale=0.28,
            fg=(0.55, 0.85, 1.0, 1), shadow=(0, 0, 0, 0.6),
            align=TextNode.ACenter,
        )
        self.subtitle = OnscreenText(
            parent=self.frame, text="a twin-stick dungeon shooter",
            pos=(0, 0.30), scale=0.06, fg=(0.75, 0.78, 0.85, 1),
            align=TextNode.ACenter,
        )

        self.start_btn = DirectButton(
            parent=self.frame, text="Start", pos=(0, 0, 0.02), scale=0.11,
            pad=(0.5, 0.3), text_fg=(1, 1, 1, 1), relief=1,
            frameColor=(
                (0.18, 0.45, 0.75, 1),   # normal
                (0.30, 0.65, 1.00, 1),   # pressed
                (0.26, 0.58, 0.92, 1),   # hover
                (0.12, 0.20, 0.30, 1),   # disabled
            ),
            command=self._start,
        )
        self.quit_btn = DirectButton(
            parent=self.frame, text="Quit", pos=(0, 0, -0.28), scale=0.085,
            pad=(0.6, 0.3), text_fg=(0.9, 0.9, 0.95, 1), relief=1,
            frameColor=(
                (0.20, 0.20, 0.24, 1),
                (0.35, 0.35, 0.40, 1),
                (0.28, 0.28, 0.33, 1),
                (0.12, 0.12, 0.14, 1),
            ),
            command=app.userExit,
        )

        self.hint = OnscreenText(
            parent=self.frame,
            text="WASD move     Mouse aim     Left click shoot     Shift sprint     Space jump",
            pos=(0, -0.7), scale=0.045, fg=(0.65, 0.67, 0.72, 1),
            align=TextNode.ACenter,
        )

    def _start(self):
        self.destroy()
        self.on_start()

    def destroy(self):
        self.frame.destroy()   # destroys all child gui as well


class PauseMenu:
    """In-game pause overlay. Esc toggles it; the mouse is released while it's
    up so the buttons are clickable."""

    def __init__(self, app, on_resume, on_quit):
        self.frame = DirectFrame(
            parent=app.aspect2d,
            frameColor=(0.04, 0.05, 0.08, 0.72),
            frameSize=(-2.0, 2.0, -1.0, 1.0),
        )
        self.title = OnscreenText(
            parent=self.frame, text="Paused", pos=(0, 0.4), scale=0.16,
            fg=(0.8, 0.9, 1.0, 1), shadow=(0, 0, 0, 0.6),
            align=TextNode.ACenter,
        )
        self.resume_btn = DirectButton(
            parent=self.frame, text="Resume", pos=(0, 0, 0.05), scale=0.1,
            pad=(0.5, 0.3), text_fg=(1, 1, 1, 1), relief=1,
            frameColor=(
                (0.18, 0.45, 0.75, 1), (0.30, 0.65, 1.00, 1),
                (0.26, 0.58, 0.92, 1), (0.12, 0.20, 0.30, 1),
            ),
            command=on_resume,
        )
        self.quit_btn = DirectButton(
            parent=self.frame, text="Quit to Menu", pos=(0, 0, -0.25), scale=0.08,
            pad=(0.6, 0.3), text_fg=(0.9, 0.9, 0.95, 1), relief=1,
            frameColor=(
                (0.20, 0.20, 0.24, 1), (0.35, 0.35, 0.40, 1),
                (0.28, 0.28, 0.33, 1), (0.12, 0.12, 0.14, 1),
            ),
            command=on_quit,
        )
        self.hint = OnscreenText(
            parent=self.frame, text="Press Esc to resume", pos=(0, -0.6),
            scale=0.045, fg=(0.65, 0.67, 0.72, 1), align=TextNode.ACenter,
        )

    def destroy(self):
        self.frame.destroy()
