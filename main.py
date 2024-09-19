import pygame
import pygame.locals
from constants import Window, Platforms
from obstacles import Platform, Baseball
from player import Player
import random
import time
import threading
#TODO
# Bases 

pygame.init()
pygame.display.set_caption("Base Dash")  # sets the window title
screen = pygame.display.set_mode(Window.SIZE)  # creates game screen
spriteSurf = pygame.Surface(Window.SIZE)
screen.fill((0, 0, 0))
clock = pygame.time.Clock()  # set up clock
gameover = False  # variable to run our game loop
player = Player((0,0))
allSprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
walls = pygame.sprite.Group()
balls = pygame.sprite.Group()
allSprites.add(player)
jitter = pygame.Vector2(0,0)
while len(platforms.sprites()) < Platforms.TOTAL_PLATFORMS:
            x = random.randint(0, Window.SIZE[0])
            y = random.randint(0, Window.SIZE[1])
            platforms.add(Platform(pygame.Vector2(x,y), random.randint(3, 15), random.randint(2,5), platforms, walls))


def summonPlatforms():
    while 1:
        while len(platforms.sprites()) < Platforms.TOTAL_PLATFORMS:
            x = Window.SIZE[0]
            y = random.randint(0, Window.SIZE[1])
            platforms.add(Platform(pygame.Vector2(x,y), random.randint(3, 15), random.randint(2, 5), platforms, walls))
        time.sleep(0)
def summonBaseballs():
    while 1:
        balls.add(Baseball(random.randint(0,Window.SIZE[1])))
        time.sleep(random.uniform(1,3))
platformThread = threading.Thread(target=summonPlatforms)
platformThread.start()
baseballThread = threading.Thread(target=summonBaseballs)
baseballThread.start()

while not gameover:  # GAME LOOP############################################################
    clock.tick(60)  # FPS
    oldTime = pygame.time.get_ticks()
    gameEvents = pygame.event.get()
    # Input Section------------------------------------------------------------
    for event in gameEvents:  # quit game if x is pressed in top corner
        if event.type == pygame.QUIT:
            gameover = True
    # RENDER Section--------------------------------------------------------------------------------a
    screen.fill((0, 0, 0))  # wipe screen so it doesn't smear
    spriteSurf.fill((0,0,0))
    platforms.update()
    walls.update()
    player.update(gameEvents, platforms, walls, balls)
    balls.update(spriteSurf)
    walls.draw(spriteSurf)
    platforms.draw(spriteSurf)
    allSprites.draw(spriteSurf)
    balls.draw(spriteSurf)
    spriteSurf = pygame.transform.scale(spriteSurf, Window.SIZE)
    screen.blit(spriteSurf, (jitter.x, jitter.y))
    pygame.display.flip()  # this actually puts the pixel on the screen
# end game loop------------------------------------------------------------------------------
pygame.quit()

