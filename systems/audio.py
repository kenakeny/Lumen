"""Central sound manager: loads the SFX bank + ambient music and exposes a
tiny ``play(name)`` API. Files live in assets/audio/. To swap a sound, edit the
filename in SFX_FILES / MUSIC_FILE below."""

from config import SFX_VOLUME, MUSIC_VOLUME

# game event name -> file in assets/audio/
SFX_FILES = {
    "shoot":         "shoot.wav",
    "enemy_damaged": "enemy_damaged.mp3",   # enemies die in one hit
    "orb_pickup":    "orb_pickup.mp3",
    "ouch":          "Ouch.mp3",            # player takes damage
}
MUSIC_FILE = "music.mp3"


class AudioManager:
    def __init__(self, app):
        self.app = app
        self.sfx = {}
        for name, filename in SFX_FILES.items():
            sound = app.loader.loadSfx(f"assets/audio/{filename}")
            if sound:
                sound.setVolume(SFX_VOLUME)
                self.sfx[name] = sound

        self.music = app.loader.loadMusic(f"assets/audio/{MUSIC_FILE}")
        if self.music:
            self.music.setLoop(True)
            self.music.setVolume(MUSIC_VOLUME)

    def play(self, name):
        """Fire a one-shot sound. Retriggers from the start if already playing
        (fine for rapid fire); unknown names are ignored."""
        sound = self.sfx.get(name)
        if sound:
            sound.play()

    def start_music(self):
        if self.music:
            self.music.play()

    def stop_music(self):
        if self.music:
            self.music.stop()

    def destroy(self):
        self.stop_music()
        for sound in self.sfx.values():
            sound.stop()
