import math
import copy
import pygame

from Body_class import Body
from Vector_class import Vector

pygame.init()
clock = pygame.time.Clock()
screen_dims = (1920, 1080)
screen = pygame.display.set_mode(screen_dims, pygame.FULLSCREEN)

G = 30000
Q = 30000

bodies = list()
players = list()
active_players = list()
in_play = False

bodies.append(Body((int(screen_dims[0] / 2 + 300), int(screen_dims[1] / 2)), θ=None, m=160, r=40, body_type="star", threat_to=("player", "pellet", "shrapnel", "bullet", "blast"), damage=5))
bodies.append(Body((int(screen_dims[0] / 2 - 300), int(screen_dims[1] / 2)), θ=None, m=160, r=40, body_type="star", threat_to=("player", "pellet", "shrapnel", "bullet", "blast"), damage=5))
player1 = Body((200, 200), r=10, friction=(1 / 400, 5), body_type="player", shot_type="shotgun",
               update_type=1, threat_reqs={"t": 150}, threat_to=("pellet", "shrapnel", "bullet", "blast", "sword"), damage=5,
               threatened_by=("pellet", "shrapnel", "bullet", "blast", "sword", "star"), health=5, self_destruct={"s": True},
               player_controls=((pygame.K_w, 250), (pygame.K_a, -30), (pygame.K_s, -50), (pygame.K_d, 30), (pygame.K_LSHIFT, 300), pygame.K_r), colour=(200, 255, 200), dark_colour=(100, 164, 100))
player2 = Body((screen_dims[0] - 200, screen_dims[1] - 200), θ=math.pi, r=10, friction=(1 / 400, 5), body_type="player", shot_type="shotgun",
               update_type=1, threat_reqs={"t": 150}, threat_to=("pellet", "shrapnel", "bullet", "blast", "sword"), damage=5,
               threatened_by=("pellet", "shrapnel", "bullet", "blast", "sword", "star"), health=5, self_destruct={"s": True},
               player_controls=((pygame.K_UP, 250), (pygame.K_LEFT, -30), (pygame.K_DOWN, 50), (pygame.K_RIGHT, 30), (pygame.K_RCTRL, 300), pygame.K_RETURN), colour=(200, 200, 255), dark_colour=(100, 100, 164))
player3 = Body((screen_dims[0] - 200, 200), θ=math.pi, r=10, friction=(1 / 400, 5), body_type="player", shot_type="sniper",
               update_type=1, threat_reqs={"t": 150}, threat_to=("pellet", "shrapnel", "bullet", "blast", "sword"), damage=5,
               threatened_by=("pellet", "shrapnel", "bullet", "blast", "sword", "star"), health=5, self_destruct={"s": True},
               player_controls=((pygame.K_i, 250), (pygame.K_j, -30), (pygame.K_k, 50), (pygame.K_l, 30), (pygame.K_n, 300), pygame.K_p), colour=(200, 255, 255), dark_colour=(100, 164, 164))
player4 = Body((200, screen_dims[1] - 200), r=10, friction=(1 / 400, 5), body_type="player", shot_type="blaster",
               update_type=1, threat_reqs={"t": 150}, threat_to=("pellet", "shrapnel", "bullet", "blast", "sword"), damage=5,
               threatened_by=("pellet", "shrapnel", "bullet", "blast", "sword", "star"), health=5, self_destruct={"s": True},
               player_controls=((pygame.K_t, 250), (pygame.K_f, -30), (pygame.K_g, 50), (pygame.K_h, 30), (pygame.K_c, 300), pygame.K_u), colour=(255, 200, 255), dark_colour=(164, 100, 164))

players.append(player1)
players.append(player2)
players.append(player3)
players.append(player4)

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
            screen = pygame.display.set_mode(screen_dims, pygame.FULLSCREEN)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True

    for player in players:
        if player in bodies:
            if keys[player.player_controls[4][0]] and (player.age - player.shot_age) >= player.shot_cooldown:
                player.fire(bodies)
        elif player in active_players:
            if player.default():
                bodies.append(player)
            else:
                active_players.remove(player)
                if len(active_players) in (0, 1):
                    in_play = False
                    for player in active_players:
                        bodies.remove(player)
                    for player in players:
                        player.stocks = 3
                    active_players = list()

        elif keys[player.player_controls[5]]:
            if len(active_players) == 1:
                in_play = True
                for other_player in players:
                    if player != other_player:
                        player.stocks = 3
            active_players.append(player)

    for body in bodies:
        body.update(1 / FPS, bodies, G, Q, keys)
    for body in bodies:
        body.step(bodies, screen_dims)

    screen.fill((0, 0, 0))
    for body in bodies:
        body.draw(screen, bodies)
    pygame.display.flip()
    clock.tick(FPS)
    frame += 1
