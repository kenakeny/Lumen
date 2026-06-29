from panda3d.core import BitMask32

PLAYER_SPEED = 7
SPRINT_MULTIPLIER = 1.8
CAM_DISTANCE = 10
CAM_HEIGHT = 1.5     # look-at height on the character (chest level)
CAM_PITCH = 35       # resting downward tilt, degrees
CAM_DAMPING = 5

ORB_SCORE_VALUE = 10

GRAVITY = 20
JUMP_SPEED = 8

ROOM_SIZE = 10
WALL_HEIGHT = 4
WALL_THICKNESS = 0.4
DOOR_WIDTH = 3
DUNGEON_GRID = 7
DUNGEON_ROOMS = 15

ENEMY_SPEED = 2.5
ENEMY_CHASE_SPEED = 5
ENEMY_DETECT_RANGE = 12
ENEMY_DAMAGE = 10
ENEMY_DAMAGE_COOLDOWN = 1.0

HAZARD_DAMAGE_PER_SEC = 15

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
