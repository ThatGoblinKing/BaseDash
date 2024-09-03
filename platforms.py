from typing import Any
import pygame
from pygame.sprite import Sprite
import constants
from constants import Platforms, Window
from pygame import Vector2
import math

class Platform(Sprite):
    def __init__(self, pos: Vector2, segments: int, speed : int, platforms : pygame.sprite.Group) -> None:
        super().__init__()
        pos.y = round(pos.y / (Platforms.SEGMENT_SIZE * Platforms.GAP)) * Platforms.SEGMENT_SIZE * Platforms.GAP
        self.platforms = platforms
        self.speed = speed
        self.segments = segments
        self.image = pygame.Surface((Platforms.SEGMENT_SIZE * segments, Platforms.SEGMENT_SIZE))
        self.image.fill(Platforms.COLOR)
        pygame.draw.rect(self.image,
                         Platforms.COLOR,
                         pygame.Rect(pos, (Platforms.SEGMENT_SIZE * segments, Platforms.SEGMENT_SIZE)))
        self.rect = pygame.Rect(pos, (Platforms.SEGMENT_SIZE * segments, Platforms.SEGMENT_SIZE))
        if len(list(pygame.sprite.spritecollide(self, self.platforms, False))) > 0:
            self.kill()
    def update(self, *args: Any, **kwargs: Any) -> None:
        self.rect.x -= self.speed
        collidingPlatforms = pygame.sprite.spritecollide(self, self.platforms, False)
        for platform in (platform for platform in collidingPlatforms if platform is not self):
            tempSpeed = self.speed
            self.speed = platform.speed
            platform.speed = tempSpeed
            if self.rect.left > Window.SIZE[0]:
                self.kill()
        if self.rect.right < 0:
            self.kill()
        return super().update(*args, **kwargs)