# Lumen

A top-down-ish twin-stick dungeon crawler built with [Panda3D](https://www.panda3d.org/).
Explore a simple procedurally generated dungeon, grab glowing orbs for score, dodge
hazards, and gun down enemies that hunt you down.

## Gameplay

- **Orbs** — collect them for points.
- **Enemies** — patrol their rooms until they spot you, then give chase. Shoot
  them down before they reach you. They keep spawning over time, so it never
  fully clears out.
- **Hazards** — glowing floor zones that burn you while you stand in them.
- **Score** — earned from orbs and kills, shown on the HUD alongside your health.

## Controls

| Input | Action |
| --- | --- |
| **W A S D** | Move (relative to where you're aiming) |
| **Mouse** | Aim / look, the camera and crosshair follow the mouse |
| **Left click** | Shoot |
| **Mouse wheel** | Zoom in / out |
| **Space** | Jump |
| **Shift** | Sprint |

Aiming, facing, and movement are all driven by the camera's forward direction, so the crosshair always marks exactly where your shots go including up and down when you tilt the view.

## Requirements

- Python 3.10+
- [Panda3D](https://www.panda3d.org/) 1.10+

## Running

```bash
# install the one dependency
pip install panda3d

# launch the game
python main.py
```

## Project layout

| Path | What's in it |
| --- | --- |
| `app.py` | Main `App` class — wires everything together and runs the game loop |
| `config.py` | Tunable constants (speeds, camera, spawning, collision masks) |
| `player/` | Player movement, the follow/aim camera |
| `world/` | Dungeon generation, rooms, lighting |
| `entities/` | Orbs, enemies, hazards |
| `systems/` | Collision, combat, scoring, audio, save |
| `ui/` | HUD and menus |
| `utils/` | Math helpers |
| `tests/` | Unit tests |

## Credits

Models:

1. [Wezu's p3d_samples](https://github.com/wezu/p3d_samples/tree/master/models), the amazing Panda-Chan model.
2. [ArsThaumaturgis's PandaSampleModels](https://github.com/ArsThaumaturgis/PandaSampleModels), other models like the walls of the dungeon  

Audio:
1. Obtaining orb sound: Item Get Inorganic.wav by SilverIllusionist -- https://freesound.org/s/411171/ -- License: Attribution 4.0
2. Shoot sound: Laser FX #3 by danlucaz -- https://freesound.org/s/517763/ -- License: Creative Commons 0
3. Damage sound effect: Damage sound effect by Raclure -- https://freesound.org/s/458867/ -- License: Creative Commons 0
4. Ouch: Ouch ! by Legnalegna55 -- https://freesound.org/s/547344/ -- License: Creative Commons 0
5. Ambient music: Ambient electronic music 001 by frankum -- https://freesound.org/s/328368/ -- License: Attribution 4.0
## License

Released under the [MIT License](LICENSE).
