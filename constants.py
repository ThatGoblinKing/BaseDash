class Window:
    SIZE = (1280, 720)

class Player:
    SIZE = (25, 40)
    COLOR = (255,255,255)
    MOVE_SPEED = 4
    JUMP_FORCE = 8
    JUMP_CONTROL = .2
    DASH_SPEED = 15
    DASH_FALLOFF = 0.7
    SWING_TIME = 200 #Milliseconds
    SWING_COOLDOWN = 500
class Physics:
    GRAVITY = .25
    TERMINAL_VELOCITY = 15
    FRICTION = .5
    COLLISION_MARGIN_OF_ERROR = 17
    COYOTE_TIME = 250 #milliseconds of jump allowance after walking off a platform

class Input:
    LEFT, RIGHT, UP, DOWN = (0, 1, 2 ,3)

class Platforms:
    SEGMENT_SIZE = 25
    COLOR = (0,255,255)
    GAP = 4
    TOTAL_PLATFORMS = 10

class Wall:
    COLOR = (255,0,0)
    CHANCE = 10
    
class Balls:
    ANGLE_VARIANCE = 25
    SPEED = 5
    HIT_SPEED = -20
    SIZE = (15, 15)
    COLOR = (255,0,0)