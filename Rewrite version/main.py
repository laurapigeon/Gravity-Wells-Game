import math
import pygame

from Body_class import Body
from Vector_class import Vector

import Config as c

pygame.init()

screen_size = (1280, 720)
screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
clock = pygame.time.Clock()

bodies = list()

s1 = 50
s2 = 80
P1 = Vector(300, 360)
P2 = P1 - Vector(0, s1)
m1 = 100
m2 = 20
v2 = math.sqrt((c.GRAV * m1) * (2 / s1 - 1 / s2))

bodies.append(Body(ipos=[P1, Vector(0, 0)], imass=[m1], iradius=[4]))
bodies.append(Body(ipos=[P2, Vector(v2, 0)], imass=[m2], iradius=[4]))

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

    screen.fill((0, 0, 0))

    Body.update_bodies(screen, c.DT, bodies)

    Body.draw_bodies(screen, bodies)

    pygame.display.flip()
    clock.tick(1 / c.DT)
    frame += 1
