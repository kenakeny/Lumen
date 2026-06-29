from panda3d.core import BitMask32

PLAYER_SPEED = 7
SPRINT_MULTIPLIER = 1.8
CAM_DISTANCE = 9
CAM_HEIGHT = 1.8     # look-at height on the character (head/shoulder level)
CAM_PITCH = 12       # resting downward tilt, degrees (low, behind-the-shoulder)
CAM_DAMPING = 9

ORB_SCORE_VALUE = 10

GRAVITY = 20
JUMP_SPEED = 8

ROOM_SIZE = 24
WALL_HEIGHT = 4
WALL_THICKNESS = 0.4
DOOR_WIDTH = 4
DUNGEON_GRID = 7
DUNGEON_ROOMS = 15

ENEMY_SPEED = 2.5
ENEMY_CHASE_SPEED = 5
ENEMY_DETECT_RANGE = 12
ENEMY_DAMAGE = 10
ENEMY_DAMAGE_COOLDOWN = 1.0

HAZARD_DAMAGE_PER_SEC = 15

# spawning: initial counts, live caps, and how often new ones appear
ORB_INITIAL_COUNT = 10
ORB_MAX = 18
ORB_SPAWN_INTERVAL = 5.0

ENEMY_INITIAL_COUNT = 8
ENEMY_MAX = 14
ENEMY_SPAWN_INTERVAL = 7.0
SPAWN_MARGIN = 3.0          # keep spawns this far from room walls
ENEMY_SPAWN_SAFE_DIST = 20  # don't spawn enemies this close to the player

PROJECTILE_SPEED = 18
PROJECTILE_LIFETIME = 3.0
PROJECTILE_DAMAGE = 50
SHOOT_COOLDOWN = 0.3
ENEMY_KILL_SCORE = 25


class Masks:
    EMPTY       = BitMask32(0)
    PLAYER      = BitMask32.bit(0)
    ORB         = BitMask32.bit(1)
    HAZARD      = BitMask32.bit(2)
    ENEMY       = BitMask32.bit(3)
    WALL        = BitMask32.bit(4)
    FLOOR       = BitMask32.bit(5)
    PROJECTILE  = BitMask32.bit(6)
