import pygame
from pygame.sprite import Sprite
import constants
from constants import Physics, Input, Window
from pygame import Vector2

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
        self.startCoyote = 0

    def update(self, events: list[pygame.event.Event], platforms: pygame.sprite.Group):
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
        self.rect.center += Vector2(self.velocity.x + self.moveX, self.velocity.y)
        # print(f"Regular Jump: {self.canCoyote}, Double Jump: {self.canDouble}")
        if self.groundPlatform is not None:
            self.velocity.x = -self.groundPlatform.speed
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

        if self.canCoyote and pygame.time.get_ticks() > self.startCoyote + Physics.COYOTE_TIME:
            self.canCoyote = False
            # print("COYOTE OVER")
        if not self.grounded:
            self.velocity.x = 0
        # print(pygame.time.get_ticks())
        collidingPlatforms = pygame.sprite.spritecollide(self, platforms, False)
        if self.rect.right > Window.SIZE[0]:
            self.rect.right = Window.SIZE[0]

        for platform in collidingPlatforms:
            # print(collidingPlatforms)
            if self.rect.bottom > platform.rect.top and abs(self.rect.bottom - platform.rect.top) < Physics.COLLISION_MARGIN_OF_ERROR:
                self.velocity.x = -platform.speed
                self.startCoyote = pygame.time.get_ticks() + Physics.COYOTE_TIME + 100000
                self.rect.bottom = platform.rect.top
                self.velocity.y = 0
                self.grounded = True
                self.groundPlatform = platform
                self.canCoyote = True
                self.canDouble = True
            elif self.rect.top < platform.rect.bottom and abs(self.rect.top - platform.rect.bottom) < Physics.COLLISION_MARGIN_OF_ERROR:
                self.rect.top = platform.rect.bottom
                self.velocity.y = 0
            elif self.rect.right > platform.rect.left and abs(self.rect.right - platform.rect.left) < Physics.COLLISION_MARGIN_OF_ERROR:
                self.rect.right = platform.rect.left
                self.velocity.x = 0
                self.xInput = 0
            elif self.rect.left < platform.rect.right and abs(self.rect.left - platform.rect.right) < Physics.COLLISION_MARGIN_OF_ERROR:
                self.rect.left = platform.rect.right
                self.velocity.x = 0
                self.xInput = 0