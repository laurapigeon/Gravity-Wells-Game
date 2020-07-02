import pygame

from Body_class import Body

import Config as c

pygame.init()

screen_size = (1280, 720)
screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
clock = pygame.time.Clock()

bodies = list()

done = False
frame = 0
while not done:
    events = pygame.event.get()
    presses = pygame.key.get_pressed()
    for event in events:
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.VIDEORESIZE:
            screen_size = (event.w, event.h)
            screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True

    Body.update_bodies(c.DT, bodies)

    screen.fill((0, 0, 0))

    Body.draw_bodies(screen, bodies)

    pygame.display.flip()
    clock.tick(1 / c.DT)
    frame += 1
