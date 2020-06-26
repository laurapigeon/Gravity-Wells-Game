import math
import copy
import pygame

from Body_class import Body
from Vector_class import Vector

pygame.init()
clock = pygame.time.Clock()
screen_dims = (1920, 1020)
screen = pygame.display.set_mode(screen_dims, pygame.RESIZABLE)

G = 30000

bodies = list()
players = list()
bodies.append(Body((int(screen_dims[0] / 2 + 300), int(screen_dims[1] / 2)), θ=None, m=160, r=40, body_type="star", threat_to=("player", "bullet"), damage=3))
bodies.append(Body((int(screen_dims[0] / 2 - 300), int(screen_dims[1] / 2)), θ=None, m=160, r=40, body_type="star", threat_to=("player", "bullet"), damage=3))
player1 = Body((200, 200), m=0, r=10, friction=(1 / 400, 5),
               body_type="player", update_type=10, threat_to=("bullet"), damage=1, threatened_by=("bullet", "star"), health=3, self_destruct={"s": True}, ammo=3,
               player_controls=((pygame.K_e, 200), (pygame.K_s, -30), (pygame.K_d, -50), (pygame.K_f, 30), (pygame.K_SPACE, 300), pygame.K_t))
player2 = Body((screen_dims[0] - 200, screen_dims[1] - 200), m=0, r=10, friction=(1 / 400, 5),
               body_type="player", update_type=10, threat_to=("bullet"), damage=1, threatened_by=("bullet", "star"), health=3, self_destruct={"s": True}, ammo=3,
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
            screen_dims = (event.w, event.h)
            screen = pygame.display.set_mode(screen_dims, pygame.RESIZABLE)

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
        body.step(bodies, screen_dims)

    screen.fill((0, 0, 0))
    for body in bodies:
        body.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
    frame += 1
