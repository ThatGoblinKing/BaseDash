import pygame
from constants import Window, Platforms
from obstacles import Platform
from player import Player
import random
import time
import threading
#TODO
# Baseballs
# Hit the baseballs
# Bases
# Walls

pygame.init()
pygame.display.set_caption("Base Dash")  # sets the window title
screen = pygame.display.set_mode(Window.SIZE)  # creates game screen
screen.fill((0, 0, 0))
clock = pygame.time.Clock()  # set up clock
gameover = False  # variable to run our game loop
player = Player((0,0))
allSprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
walls = pygame.sprite.Group()
allSprites.add(player)
while len(platforms.sprites()) < Platforms.TOTAL_PLATFORMS:
            x = random.randint(0, Window.SIZE[0])
            y = random.randint(0, Window.SIZE[1])
            platforms.add(Platform(pygame.Vector2(x,y), random.randint(3, 15), random.randint(2, 5), platforms, walls))
# for i in range(0, Window.SIZE[1], 60):
#      platforms.add(Platform(pygame.Vector2(Window.SIZE[0], i), 10, 5, platforms))


def summonPlatforms():
    while 1:
        while len(platforms.sprites()) < Platforms.TOTAL_PLATFORMS:
            x = Window.SIZE[0]
            y = random.randint(0, Window.SIZE[1])
            platforms.add(Platform(pygame.Vector2(x,y), random.randint(3, 15), random.randint(2, 5), platforms, walls))
        time.sleep(0)
platformThread = threading.Thread(target=summonPlatforms)
platformThread.start()

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
    platforms.update()
    walls.update()
    player.update(gameEvents, platforms, walls)
    walls.draw(screen)
    platforms.draw(screen)
    allSprites.draw(screen)
    
    pygame.display.flip()  # this actually puts the pixel on the screen
# end game loop------------------------------------------------------------------------------
pygame.quit()

