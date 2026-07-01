from panda3d.core import BitMask32

PLAYER_SPEED = 7
SPRINT_MULTIPLIER = 1.8
CAM_DISTANCE = 9
CAM_HEIGHT = 1.8       # look-at height on the character (head/shoulder level)
CAM_ELEV = -12        # resting view elevation, degrees (negative = looking down)
CAM_ELEV_MIN = -75    # how far down you can aim
CAM_ELEV_MAX = 60     # how far up you can aim
CAM_SENSITIVITY = 0.06  # degrees of rotation per pixel of mouse motion
CAM_DAMPING = 9

ORB_SCORE_VALUE = 10

GRAVITY = 20
JUMP_SPEED = 8

KNOCKBACK_FORCE = 10      # initial knockback speed (units/sec)
KNOCKBACK_DAMPING = 9     # how quickly knockback decays

ROOM_SIZE = 24
WALL_HEIGHT = 4
WALL_THICKNESS = 0.4
DOOR_WIDTH = 4
DUNGEON_GRID = 7
DUNGEON_ROOMS = 15

ENEMY_SPEED = 2.5
ENEMY_CHASE_SPEED = 5
ENEMY_DETECT_RANGE = 12        # acquire the player within this range
ENEMY_LOSE_RANGE = 16          # give up the chase past this range (hysteresis)
ENEMY_DAMAGE = 10
ENEMY_DAMAGE_COOLDOWN = 1.0

# attack state (telegraphed lunge)
ENEMY_ATTACK_RANGE = 2.5       # close enough to wind up an attack
ENEMY_ATTACK_WINDUP = 0.4      # telegraph time before the lunge
ENEMY_ATTACK_LUNGE_SPEED = 16
ENEMY_ATTACK_LUNGE_TIME = 0.22
ENEMY_ATTACK_COOLDOWN = 0.8    # recover time after a lunge
ENEMY_SEARCH_TIME = 3.0        # how long to hunt the last-seen spot before giving up

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

# audio (0.0 - 1.0)
SFX_VOLUME = 0.6
MUSIC_VOLUME = 0.35


class Masks:
    EMPTY       = BitMask32(0)
    PLAYER      = BitMask32.bit(0)
    ORB         = BitMask32.bit(1)
    HAZARD      = BitMask32.bit(2)
    ENEMY       = BitMask32.bit(3)
    WALL        = BitMask32.bit(4)
    FLOOR       = BitMask32.bit(5)
    PROJECTILE  = BitMask32.bit(6)
