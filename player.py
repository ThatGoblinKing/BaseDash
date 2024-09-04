import pygame
from pygame.sprite import Sprite
import constants
from constants import Physics, Input, Window
from pygame import Vector2
from obstacles import Platform, Wall
class Player(Sprite):
    def __init__(self, pos: Vector2) -> None:
        super().__init__()
        self.pos = pos
        self.image = pygame.Surface(constants.Player.SIZE)
        self.image.fill(constants.Player.COLOR)
        pygame.draw.rect(self.image,
                         constants.Player.COLOR,
                         pygame.Rect(pos, constants.Player.SIZE))
        self.rect = self.image.get_rect()
        self.velocity : Vector2 = Vector2(0,0)
        self.pressedKeys = [False, False, False, False]
        self.xInput : int = 0
        self.moveX : int = 0
        self.grounded = False
        self.groundPlatform : pygame.Rect = None
        self.canDouble = True
        self.canCoyote = False
        self.canDash = True
        self.startCoyote = 0
        self.dashVel = 0
        self.oldRect = self.rect.copy()

    def update(self, events: list[pygame.event.Event], platforms: pygame.sprite.Group, walls: pygame.sprite.Group):
        self.oldRect = self.rect.copy()
        self.velocity.y += (Physics.GRAVITY if self.velocity.y < Physics.TERMINAL_VELOCITY and not self.grounded else 0)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.pressedKeys[Input.LEFT] = True
                if event.key == pygame.K_d:
                    self.pressedKeys[Input.RIGHT] = True
                if event.key == pygame.K_SPACE and (self.canDouble or self.canCoyote):
                    self.pressedKeys[Input.UP] = True
                    self.velocity.y = 0
                    self.velocity.y -= constants.Player.JUMP_FORCE
                    self.grounded = False
                    self.canDouble = False if self.canCoyote == False else self.canDouble
                    self.canCoyote = False
                if event.key == pygame.K_LSHIFT and self.canDash:
                    self.dashVel = constants.Player.DASH_SPEED
                    self.canDash = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.pressedKeys[Input.LEFT] = False
                if event.key == pygame.K_d:
                    self.pressedKeys[Input.RIGHT] = False
                if event.key == pygame.K_SPACE:
                    self.pressedKeys[Input.UP] = False

        self.xInput = 0 if self.pressedKeys[Input.LEFT] == self.pressedKeys[Input.RIGHT] else -1 if self.pressedKeys[Input.LEFT] else 1
        self.moveX += (self.xInput * constants.Player.MOVE_SPEED) - (self.moveX * Physics.FRICTION) 
        self.moveX = pygame.math.clamp(self.moveX, -constants.Player.MOVE_SPEED, constants.Player.MOVE_SPEED)
        if self.moveX > 0 and self.xInput == 1:
            self.moveX -= self.velocity.x
        if not self.pressedKeys[Input.UP] and not self.grounded and self.velocity.y < 0:
            self.velocity.y = pygame.math.lerp(self.velocity.y, 0, constants.Player.JUMP_CONTROL)
        self.rect.center += Vector2(self.velocity.x + self.moveX + self.dashVel, self.velocity.y)
        # print(f"Regular Jump: {self.canCoyote}, Double Jump: {self.canDouble}")
        if self.groundPlatform is not None:
            self.velocity.x = -self.groundPlatform.speed 
            self.canDash = True
            if self.rect.left > self.groundPlatform.rect.right:
                self.startCoyote = pygame.time.get_ticks()
                self.grounded = False
                self.groundPlatform = None
                # print("COYOTE START")
            elif self.rect.right < self.groundPlatform.rect.left:
                self.startCoyote = pygame.time.get_ticks()
                self.grounded = False
                self.groundPlatform = None
                # print("COYOTE START")
        if self.dashVel != 0:
            self.dashVel -= constants.Player.DASH_FALLOFF
            self.velocity.y = 0
        if self.dashVel < 0:
            self.dashVel = 0

        if self.canCoyote and pygame.time.get_ticks() > self.startCoyote + Physics.COYOTE_TIME:
            self.canCoyote = False
            # print("COYOTE OVER")
        if not self.grounded:
            self.velocity.x = 0

        if self.rect.right > Window.SIZE[0]:
            self.rect.right = Window.SIZE[0]

        collidingPlatforms = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collidingPlatforms:
            if self.rect.right >= platform.rect.left and self.oldRect.right <= platform.oldRect.left:
                self.rect.right = platform.rect.left
                self.velocity.x = 0
                self.xInput = 0
                self.dashVel = 0
            elif self.rect.left <= platform.rect.right and self.rect.left >= platform.rect.right:
                self.rect.left = platform.rect.right
                self.velocity.x = 0
                self.xInput = 0
                self.dashVel = 0

        for platform in collidingPlatforms:
            if self.rect.bottom >= platform.rect.top and self.oldRect.bottom <= platform.oldRect.top:
                self.velocity.x = -platform.speed
                self.startCoyote = pygame.time.get_ticks() + Physics.COYOTE_TIME + 100000
                self.rect.bottom = platform.rect.top
                self.velocity.y = 0
                self.grounded = True
                self.groundPlatform = platform
                self.canCoyote = True
                self.canDouble = True
                self.dashVel = 0 if self.dashVel < 1 else 1
                self.canDash = True
            elif self.rect.top <= platform.rect.bottom and self.oldRect.top >= platform.oldRect.bottom:
                self.rect.top = platform.rect.bottom
                self.velocity.y = 0
                
        collidingWalls = pygame.sprite.spritecollide(self, walls, False)
        for wall in collidingWalls:
            if self.rect.right > wall.rect.left and self.oldRect.right <= wall.oldRect.left:
                self.rect.right = wall.rect.left
                self.velocity.x = 0
                self.xInput = 0
                self.dashVel = 0
            elif self.rect.left < wall.rect.right and self.oldRect.left >= wall.oldRect.right:
                print("bah.")
                self.rect.left = wall.rect.right
                self.velocity.x = 0
                self.xInput = 0
                self.dashVel = 0

        for wall in collidingWalls:
            if self.rect.bottom >= wall.rect.top and self.oldRect.bottom <= wall.oldRect.top:
                self.velocity.x = -wall.speed
                self.startCoyote = pygame.time.get_ticks() + Physics.COYOTE_TIME + 100000
                self.rect.bottom = wall.rect.top
                self.velocity.y = 0
                self.grounded = True
                self.groundPlatform = wall
                self.canCoyote = True
                self.canDouble = True
                self.dashVel = 0 if self.dashVel < 1 else 1
                self.canDash = True
            elif self.rect.top <= wall.rect.bottom and self.oldRect.top >= wall.oldRect.bottom:
                self.rect.top = wall.rect.bottom
                self.velocity.y = 0