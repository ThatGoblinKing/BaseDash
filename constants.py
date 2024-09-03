class Window:
    SIZE = (1280, 720)

class Player:
    SIZE = (10, 30)
    COLOR = (255,255,255)
    MOVE_SPEED = 3
    JUMP_FORCE = 8
    JUMP_CONTROL = .2
    
class Physics:
    GRAVITY = .25
    TERMINAL_VELOCITY = 15
    FRICTION = .5
    COLLISION_MARGIN_OF_ERROR = 17
    COYOTE_TIME = 250 #milliseconds of jump allowance after walking off a platform

class Input:
    LEFT, RIGHT, UP, DOWN = (0, 1, 2 ,3)

class Platforms:
    SEGMENT_SIZE = 20
    COLOR = (0,255,255)
    GAP = 3
    TOTAL_PLATFORMS = 10