import pygame
from pygame.sprite import Sprite
from constants import Physics, Input, Window, Platforms, Player as PlayerConstants
from pygame import Vector2
from obstacles import Platform, Base
import math
from typing import Any
class Player(Sprite):
    def __init__(self, pos: Vector2) -> None:
        #Sprite Init ------------------------------------------------------
        super().__init__()
        self.image = pygame.Surface(PlayerConstants.SIZE)
        self.image.fill(PlayerConstants.COLOR)
        pygame.draw.rect(self.image,
                         PlayerConstants.COLOR,
                         pygame.Rect(pos, PlayerConstants.SIZE))
        #Appearance -------------------------------------------------------
        #Physics ----------------------------------------------------------
        self.rect : pygame.Rect = self.image.get_rect()
        self.velocity : Vector2 = Vector2(0,0)
        self.pressedKeys = [False, False, False, False]
        self.groundPlatform : Platform|None = None
        self.dashVel : float = 0
        self.oldRect : pygame.Rect = self.rect.copy()
        #Input ------------------------------------------------------------
        self.xInput : int = 0
        self.moveX : float = 0
        #Conditions -------------------------------------------------------
        self.grounded : bool = False
        self.canDoubleJump : bool = True
        self.canJump : bool = False
        self.canDash : bool = True
        self.swinging : bool = False
        self.invincible : bool = False
        #Timers -----------------------------------------------------------
        self.startCoyote : int = 0
        self.startSwing : int = 0
        self.startInvincibility : int = 0
        self.lastBase : int = 0
        #Stats ------------------------------------------------------------
        self.score : int = 0
        self.health : int = 3
        self.multiplier : int = 1

    def update(self, events: list[pygame.event.Event], platforms: pygame.sprite.Group, walls: pygame.sprite.Group, baseballs: pygame.sprite.Group):
        TIME = pygame.time.get_ticks()
        # print(int(round(self.score, -1)), self.multiplier)

        # INPUTS
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.pressedKeys[Input.LEFT] = True
                elif event.key == pygame.K_d:
                    self.pressedKeys[Input.RIGHT] = True
                elif event.key == pygame.K_SPACE and (self.canDoubleJump or self.canJump):
                    self.pressedKeys[Input.UP] = True
                    self.velocity.y = 0
                    self.velocity.y -= PlayerConstants.JUMP_FORCE
                    self.grounded = False
                    self.canDoubleJump = False if self.canJump == False else self.canDoubleJump
                    self.canJump = False
                elif event.key == pygame.K_LSHIFT and self.canDash:
                    self.dashVel = PlayerConstants.DASH_SPEED
                    self.canDash = False
                elif event.key == pygame.K_RETURN and TIME - self.startSwing > PlayerConstants.SWING_COOLDOWN:
                    self.swinging = True
                    self.startSwing = TIME
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.pressedKeys[Input.LEFT] = False
                elif event.key == pygame.K_d:
                    self.pressedKeys[Input.RIGHT] = False
                elif event.key == pygame.K_SPACE:
                    self.pressedKeys[Input.UP] = False

        self.xInput = 0 if self.pressedKeys[Input.LEFT] == self.pressedKeys[Input.RIGHT] else -1 if self.pressedKeys[Input.LEFT] else 1
        self.moveX += (self.xInput * PlayerConstants.MOVE_SPEED) - (self.moveX * Physics.FRICTION) 
        self.moveX = pygame.math.clamp(self.moveX, -PlayerConstants.MOVE_SPEED, PlayerConstants.MOVE_SPEED)
        if self.moveX > 0 and self.xInput == 1:
            self.moveX -= self.velocity.x
        if not self.pressedKeys[Input.UP] and not self.grounded and self.velocity.y < 0:
            self.velocity.y = pygame.math.lerp(self.velocity.y, 0, PlayerConstants.JUMP_CONTROL)

        # MULTIPLIER LOGIC ------------------------------------------------
        self.multiplier = pygame.math.clamp(self.multiplier, 1, 5)
        if TIME - self.lastBase > PlayerConstants.MULTIPLIER_FALLOFF / self.multiplier:
            self.multiplier = 1
        self.oldRect = self.rect.copy()
        self.score += 0.075 * self.multiplier
        print(round(self.score))


        # PLATFORM & JUMP PHYSICS  ----------------------------------------
        self.velocity.y += (Physics.GRAVITY if self.velocity.y < Physics.TERMINAL_VELOCITY and not self.grounded else 0)

        if self.groundPlatform is not None:
                    self.velocity.x = -self.groundPlatform.speed 
                    self.canDash = True
                    if self.rect.left > self.groundPlatform.rect.right:
                        self.startCoyote = TIME
                        self.grounded = False
                        self.groundPlatform = None
                    elif self.rect.right < self.groundPlatform.rect.left:
                        self.startCoyote = TIME
                        self.grounded = False
                        self.groundPlatform = None
        if not self.grounded:
            self.velocity.x = 0

        if self.canJump and TIME > self.startCoyote + Physics.COYOTE_TIME:
            self.canJump = False

        #DASH LOGIC -------------------------------------------------------
        if self.dashVel != 0:
            self.dashVel -= PlayerConstants.DASH_FALLOFF
            self.velocity.y = 0
        if self.dashVel < 0:
            self.dashVel = 0

        #SWING LOGIC ------------------------------------------------------
        if self.swinging and TIME - self.startSwing > PlayerConstants.SWING_TIME:
            self.swinging = False

        self.rect.center += Vector2(self.velocity.x + self.moveX + self.dashVel, self.velocity.y) # APPLY VELOCITY

        self.collisions(platforms, walls, baseballs, TIME) # CHECK COLLISIONS AFTER MOVING

        if self.invincible and TIME - self.startInvincibility > PlayerConstants.INVINCIBILITY_TIME:
            self.invincible = False
        self.image.set_alpha(128 if self.invincible else 255)

    def collisions(self, platforms: pygame.sprite.Group, walls: pygame.sprite.Group, baseballs: pygame.sprite.Group, TIME: int) -> None:
        if self.rect.right > Window.SIZE[0]:
            self.rect.right = Window.SIZE[0]

        collidingPlatforms = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collidingPlatforms:
            if self.rect.right > platform.rect.left and self.oldRect.right <= platform.oldRect.left:
                self.rect.right = platform.rect.left
                self.velocity.x = 0
                self.xInput = 0
                self.dashVel = 0
            if self.rect.left <= platform.rect.right and self.rect.left >= platform.rect.right - Physics.COLLISION_MARGIN_OF_ERROR:
                self.rect.left = platform.rect.right
                self.velocity.x = 0
                self.xInput = 0
                self.dashVel = 0
        for platform in collidingPlatforms:
            if self.rect.bottom >= platform.rect.top and self.oldRect.bottom <= platform.oldRect.top:
                self.velocity.x = -platform.speed
                self.startCoyote = TIME + Physics.COYOTE_TIME + 100000
                self.rect.bottom = platform.rect.top
                self.velocity.y = 0
                self.grounded = True
                self.groundPlatform = platform
                self.canJump = True
                self.canDoubleJump = True
                self.dashVel = 0 if self.dashVel < 1 else 1
                self.canDash = True
            elif self.rect.top <= platform.rect.bottom and self.oldRect.top >= platform.oldRect.bottom:
                self.rect.top = platform.rect.bottom
                self.velocity.y = 0

        collidingWalls = pygame.sprite.spritecollide(self, walls, False)
        for wall in collidingWalls:
            if self.rect.right >= wall.rect.left and self.oldRect.right <= wall.oldRect.left:
                if self.dashVel != 0 and isinstance(wall, Base):
                    wall.destroy()
                    self.multiplier += .25
                    self.lastBase = TIME
                else:
                    self.dashVel = 0
                self.rect.right = wall.rect.left
                self.velocity.x = 0
                self.xInput = 0
            elif self.rect.left <= wall.rect.right and self.oldRect.left >= wall.oldRect.right:
                self.rect.left = wall.rect.right
                self.velocity.x = 0
                self.xInput = 0
                self.dashVel = 0
            if self.rect.bottom >= wall.rect.top and self.oldRect.bottom <= wall.oldRect.top:
                self.velocity.x = -wall.speed
                self.startCoyote = TIME + Physics.COYOTE_TIME + 100000
                self.rect.bottom = wall.rect.top
                self.velocity.y = 0
                self.grounded = True
                self.groundPlatform = wall
                self.canJump = True
                self.canDoubleJump = True
                self.dashVel = 0 if self.dashVel < 1 else 1
                self.canDash = True
            elif self.rect.top <= wall.rect.bottom and self.oldRect.top >= wall.oldRect.bottom:
                self.rect.top = wall.rect.bottom
                self.velocity.y = 0

        collidingBaseballs = pygame.sprite.spritecollide(self, baseballs, False)
        for baseball in collidingBaseballs:
            if not self.swinging or baseball.rect.left < self.rect.centerx or self.invincible:
                self.invincible = True
                self.startInvincibility = TIME
                self.health -= 1
            else:
                angleTo = math.sqrt(abs(baseball.rect.left - self.rect.right) + abs(baseball.rect.bottom - (self.rect.bottom - (Platforms.SEGMENT_SIZE * 0.6))))
                if 270 > angleTo > 90:
                    angleTo *= -1
                baseball.hit(angleTo)