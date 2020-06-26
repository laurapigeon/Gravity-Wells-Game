import math
import copy
import pygame

from Body_class import Body
from Vector_class import Vector

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1920, 1020), pygame.RESIZABLE)

G = 30000

bodies = list()
players = list()
bodies.append(Body((int(1920 / 2 + 300), int(1020 / 2)), θ=None, m=160, r=40, body_type="star", threat_to=("player", "bullet")))
bodies.append(Body((int(1920 / 2 - 300), int(1020 / 2)), θ=None, m=160, r=40, body_type="star", threat_to=("player", "bullet")))
player1 = Body((200, 200), m=0, r=10, friction=(1 / 400, 5), body_type="player", update_type=20, threat_to=("player"), threatened_by=("player", "bullet", "star"),
               player_controls=((pygame.K_e, 200), (pygame.K_s, -30), (pygame.K_d, -50), (pygame.K_f, 30), (pygame.K_SPACE, 300), pygame.K_r))
player2 = Body((1920 - 200, 1020 - 200), m=0, r=10, friction=(1 / 400, 5), body_type="player", update_type=20, threat_to=("player"), threatened_by=("player", "bullet", "star"),
               player_controls=((pygame.K_UP, 200), (pygame.K_LEFT, -30), (pygame.K_DOWN, 50), (pygame.K_RIGHT, 30), (pygame.K_RCTRL, 300), pygame.K_RETURN))
players.append(player1)
players.append(player2)

done = False
frame = 1
FPS = 60
while not done:
    events = pygame.event.get()
    keys = pygame.key.get_pressed()
    for event in events:
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        if event.type == pygame.KEYDOWN:
            for player in players:
                if player in bodies:
                    if event.key == player.player_controls[4][0]:
                        player.fire(bodies)
                else:
                    if event.key == player.player_controls[5]:
                        player.default()
                        bodies.append(player)

    for body in bodies:
        body.update(1 / FPS, bodies, G, keys)
    for body in bodies:
        body.step(bodies)

    screen.fill((0, 0, 0))
    for body in bodies:
        body.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
    frame += 1
