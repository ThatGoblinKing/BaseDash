from typing import Any
import pygame
from pygame.sprite import Sprite
from constants import Platforms, Window, Wall as WallConst, Balls, Bases
from pygame import Vector2
import random

class Platform(Sprite):
    def __init__(self, pos: Vector2, segments: int, speed : int, obstacleGroup : pygame.sprite.Group, wall : pygame.sprite.Group) -> None:
        super().__init__()
        pos.y = round(pos.y / (Platforms.SEGMENT_SIZE * Platforms.GAP)) * Platforms.SEGMENT_SIZE * Platforms.GAP
        self.obstacleGroup = obstacleGroup
        self.speed = speed
        self.segments = segments
        self.image = pygame.Surface((Platforms.SEGMENT_SIZE * segments, Platforms.SEGMENT_SIZE))
        self.image.fill(Platforms.COLOR)
        pygame.draw.rect(self.image,
                         Platforms.COLOR,
                         pygame.Rect(pos, (Platforms.SEGMENT_SIZE * segments, Platforms.SEGMENT_SIZE)))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.oldRect = self.rect.copy()
        self.oldTime = 0
        if random.randint(0,100) < WallConst.CHANCE:
            wall.add(Wall(random.randint(0,segments - 1), self))
        elif random.randint(0,100) < Bases.CHANCE:
            wall.add(Base(random.randint(0,segments - 1), self))

    def update(self) -> None:
        self.oldRect = self.rect.copy()
        self.rect.x -= self.speed
        collidingPlatforms = pygame.sprite.spritecollide(self, self.obstacleGroup, False)
        for platform in (platform for platform in collidingPlatforms if platform is not self and isinstance(platform, Platform)):
            if self.rect.x >= platform.rect.x:
                if pygame.time.get_ticks() - self.oldTime < 50:
                    self.kill()
                self.rect.left = platform.rect.right
                self.oldTime = pygame.time.get_ticks()
                tempSpeed = self.speed
                self.speed = platform.speed
                platform.speed = tempSpeed
        if self.rect.right < 0:
            self.kill()
        return super().update()

class Wall(Sprite):
    def __init__(self, segment : int, platform : Platform):
        super().__init__()
        self.image = pygame.Surface((Platforms.SEGMENT_SIZE, Platforms.SEGMENT_SIZE * 2))
        self.image.fill(WallConst.COLOR)
        self.rect = self.image.get_rect()
        self.oldRect = self.rect.copy()
        self.platform = platform
        self.rect.left = self.platform.rect.left + Platforms.SEGMENT_SIZE * segment
        self.rect.bottom = self.platform.rect.top
        self.speed = self.platform.speed
        self.segment = segment

    def update(self):
        self.oldRect = self.rect.copy()
        self.speed = self.platform.speed
        self.rect.topleft = (self.platform.rect.left + Platforms.SEGMENT_SIZE * self.segment, self.platform.rect.top - Platforms.SEGMENT_SIZE * 2)
        if self.rect.right < 0 or not self.platform.alive():
            self.kill()

class Base(Wall):
    def __init__(self, segment : int, platform : Platform):
        super().__init__(segment, platform)
        self.image = pygame.Surface((Platforms.SEGMENT_SIZE, Platforms.SEGMENT_SIZE * 2))
        self.image.fill(Bases.COLOR)
        self.rect = self.image.get_rect()
        self.oldRect = self.rect.copy()
        self.platform = platform
        self.rect.left = self.platform.rect.left + Platforms.SEGMENT_SIZE * segment
        self.rect.bottom = self.platform.rect.top
        self.speed = self.platform.speed
        self.segment = segment

    def update(self):
        self.oldRect = self.rect.copy()
        self.speed = self.platform.speed
        self.rect.topleft = (self.platform.rect.left + Platforms.SEGMENT_SIZE * self.segment, self.platform.rect.top - Platforms.SEGMENT_SIZE * 2)
        if self.rect.right < 0 or not self.platform.alive():
            self.kill()

    def destroy(self):
        self.rect.size = (0,0)
        self.kill()

class Baseball(Sprite):
    def __init__(self, y : int):
        super().__init__()
        for frame in Balls.FRAMES:
            frame.set_colorkey((255,0,255))
        y = round(y / (Platforms.SEGMENT_SIZE * Platforms.GAP)) * Platforms.SEGMENT_SIZE * Platforms.GAP + (Platforms.SEGMENT_SIZE * (Platforms.GAP - 1))
        self.image = Balls.FRAMES[0]
        self.rect = self.image.get_rect()
        self.rect.centery = y
        self.rect.left = Window.SIZE[0]
        self.velocity = Vector2(Balls.SPEED, 0)
        self.currentFrame = 0
        self.afterImages = [self.rect.topleft] * Balls.AFTER_IMAGE_COUNT

    def update(self, screen: pygame.Surface):
        self.afterImages.insert(0, self.rect.topleft)
        self.afterImages.pop(4)
        self.currentFrame = 0 if self.currentFrame >= 3 else self.currentFrame + 0.25
        afterImage = Balls.FRAMES[int(self.currentFrame)].copy()
        afterImage.convert_alpha(screen)
        for i in range(len(self.afterImages)):
            afterImage.set_alpha(i / (i+1))
            screen.blit(afterImage, self.afterImages[i])
        self.image = Balls.FRAMES[int(self.currentFrame)]
        self.rect.center -= self.velocity
        if self.rect.y > Window.SIZE[1] or self.rect.y < 0 or Window.SIZE[0] < self.rect.x or self.rect.x < 0:
            self.kill()
    def hit(self, angle : float):
        self.velocity.rotate_ip(angle + random.uniform(-Balls.ANGLE_VARIANCE, Balls.ANGLE_VARIANCE))
        self.velocity.scale_to_length(Balls.HIT_SPEED)
        if self.velocity.x < 0:
            self.velocity.x *= 1