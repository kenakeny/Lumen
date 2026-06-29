from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import DirectFrame
from direct.interval.IntervalGlobal import Sequence, Wait, LerpColorScaleInterval, Func
from panda3d.core import TextNode, TransparencyAttrib


class HUD:
    def __init__(self, app):
        self.app = app
        self._feedback_seq = None

        self.hp_frame = OnscreenImage(
            image="assets/models/UI/stoneFrame.png",
            pos=(-1.1, 0, 0.85),
            scale=(0.35, 1, 0.06),
        )
        self.hp_frame.setTransparency(TransparencyAttrib.MAlpha)

        self.hp_bar = DirectFrame(
            frameColor=(0.2, 0.8, 0.2, 1),
            frameSize=(-0.3, 0.3, -0.04, 0.04),
            pos=(-1.1, 0, 0.85),
        )

        self.score_text = OnscreenText(
            text="Score: 0",
            pos=(1.3, 0.9),
            scale=0.06,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.8),
            align=TextNode.ARight,
            mayChange=True,
        )

        self.level_text = OnscreenText(
            text="Level 1",
            pos=(0, 0.92),
            scale=0.06,
            fg=(0.8, 0.8, 0.2, 1),
            shadow=(0, 0, 0, 0.8),
            align=TextNode.ACenter,
            mayChange=True,
        )

        self.hp_text = OnscreenText(
            text="100",
            pos=(-1.1, 0.83),
            scale=0.04,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.8),
            align=TextNode.ACenter,
            mayChange=True,
        )

        self.feedback = OnscreenText(
            text="",
            pos=(0, 0.2),
            scale=0.09,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.6),
            align=TextNode.ACenter,
            mayChange=True,
        )
        self.feedback.hide()

        self.combo_text = OnscreenText(
            text="",
            pos=(1.3, 0.82),
            scale=0.05,
            fg=(1, 0.8, 0.0, 1),
            shadow=(0, 0, 0, 0.8),
            align=TextNode.ARight,
            mayChange=True,
        )

    def update(self, hp, max_hp, score, level=1, multiplier=1):
        ratio = max(0, hp / max_hp)
        self.hp_bar["frameSize"] = (-0.3 * ratio, 0.3 * ratio, -0.04, 0.04)
        offset = 0.3 * (1 - ratio)
        self.hp_bar.setX(-1.1 - offset)

        if ratio > 0.5:
            self.hp_bar["frameColor"] = (0.2, 0.8, 0.2, 1)
        elif ratio > 0.25:
            self.hp_bar["frameColor"] = (0.9, 0.7, 0.1, 1)
        else:
            self.hp_bar["frameColor"] = (0.9, 0.2, 0.1, 1)

        self.hp_text.setText(str(int(hp)))
        self.score_text.setText(f"Score: {score}")
        self.level_text.setText(f"Level {level}")

        if multiplier > 1:
            self.combo_text.setText(f"x{multiplier} COMBO!")
        else:
            self.combo_text.setText("")

    def show_feedback(self, text, color=(1, 1, 1, 1), duration=1.5):
        if self._feedback_seq:
            self._feedback_seq.finish()
        self.feedback.setText(text)
        self.feedback.setFg(color)
        self.feedback.setColorScale(1, 1, 1, 1)
        self.feedback.show()
        self._feedback_seq = Sequence(
            Wait(duration * 0.3),
            LerpColorScaleInterval(self.feedback, duration * 0.7, (1, 1, 1, 0)),
            Func(self.feedback.hide),
        )
        self._feedback_seq.start()

    def destroy(self):
        if self._feedback_seq:
            self._feedback_seq.finish()
        self.hp_frame.destroy()
        self.hp_bar.destroy()
        self.score_text.destroy()
        self.level_text.destroy()
        self.hp_text.destroy()
        self.feedback.destroy()
        self.combo_text.destroy()
