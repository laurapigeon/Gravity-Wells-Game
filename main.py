import math
import copy
import pygame

from Body_class import Body
from Vector_class import Vector

import Config as c

pygame.init()
clock = pygame.time.Clock()
screen_dims = (1920, 1080)
screen = pygame.display.set_mode(screen_dims, pygame.FULLSCREEN)
pygame.mouse.set_visible(False)

G = 30000
Q = 30000

bodies = list()
players = list()
active_players = list()
in_play = False
shot_types = ("gun", "shotgun", "sniper", "blaster", "melee", "flamethrower", "gravgun")

bodies.append(Body((int(screen_dims[0] / 2 + 300), int(screen_dims[1] / 2)), θ=None, m=160, r=40, body_type="star", threat_to=("player", "pellet", "shrapnel", "bullet", "blast", "flame", "mass"), damage=5))
bodies.append(Body((int(screen_dims[0] / 2 - 300), int(screen_dims[1] / 2)), θ=None, m=160, r=40, body_type="star", threat_to=("player", "pellet", "shrapnel", "bullet", "blast", "flame", "mass"), damage=5))
player1 = Body((200, 200), r=10, friction=(1 / 400, 5), body_type="player", shot_type="gun",
               update_type=1, threat_reqs={"t": 150}, threat_to=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass"), damage=5,
               threatened_by=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass", "star"), health=5, self_destruct={"s": True},
               player_controls=((pygame.K_w, 250), (pygame.K_a, -30), (pygame.K_s, -100), (pygame.K_d, 30), (pygame.K_LSHIFT, 300)), colour=(200, 255, 200), dark_colour=(100, 164, 100))
player2 = Body((screen_dims[0] - 200, screen_dims[1] - 200), θ=math.pi, r=10, friction=(1 / 400, 5), body_type="player", shot_type="gun",
               update_type=1, threat_reqs={"t": 150}, threat_to=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass"), damage=5,
               threatened_by=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass", "star"), health=5, self_destruct={"s": True},
               player_controls=((pygame.K_UP, 250), (pygame.K_LEFT, -30), (pygame.K_DOWN, -100), (pygame.K_RIGHT, 30), (pygame.K_RCTRL, 300)), colour=(200, 200, 255), dark_colour=(100, 100, 164))
player3 = Body((screen_dims[0] - 200, 200), θ=math.pi, r=10, friction=(1 / 400, 5), body_type="player", shot_type="gun",
               update_type=1, threat_reqs={"t": 150}, threat_to=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass"), damage=5,
               threatened_by=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass", "star"), health=5, self_destruct={"s": True},
               player_controls=((pygame.K_i, 250), (pygame.K_j, -30), (pygame.K_k, -100), (pygame.K_l, 30), (pygame.K_n, 300)), colour=(200, 255, 255), dark_colour=(100, 164, 164))
player4 = Body((200, screen_dims[1] - 200), r=10, friction=(1 / 400, 5), body_type="player", shot_type="gun",
               update_type=1, threat_reqs={"t": 150}, threat_to=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass"), damage=5,
               threatened_by=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass", "star"), health=5, self_destruct={"s": True},
               player_controls=((pygame.K_t, 250), (pygame.K_f, -30), (pygame.K_g, -100), (pygame.K_h, 30), (pygame.K_c, 300)), colour=(255, 200, 255), dark_colour=(164, 100, 164))

players.append(player1)
players.append(player2)
players.append(player3)
players.append(player4)

done = False
frame = 1
FPS = 60
FONT = pygame.font.SysFont("Courier", 20)

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
                if player not in bodies and player not in active_players:
                    if event.key in (player.player_controls[1][0], player.player_controls[3][0]):
                        shot_type_index = shot_types.index(player.shot_type) + (-1, 1)[event.key == player.player_controls[3][0]]
                        shot_type_index %= len(shot_types)
                        player.shot_type = shot_types[shot_type_index]
                    elif event.key == player.player_controls[4][0]:
                        if len(active_players) == 1:
                            in_play = True
                            for other_player in players:
                                if player != other_player:
                                    player.stocks = 3
                        else:
                            for player_sprite in players:
                                player_sprite.P = player_sprite.defP
                        active_players.append(player)

    for player in players:
        if player in bodies:
            if keys[player.player_controls[4][0]] and (player.age - player.shot_age) >= player.shot_cooldown:
                player.fire(bodies)
        elif player in active_players:
            if player.default():
                bodies.append(player)
            else:
                active_players.remove(player)
                if len(active_players) == 1:
                    in_play = False
                    bodies.remove(active_players[0])
                else:
                    player.P = player.defP
                for player in players:
                    player.stocks = 4
                    player.default(factor="no_P")
                active_players = list()

    if len(active_players) >= 1:
        for body in bodies:
            body.update(1 / FPS, bodies, G, Q, keys)
        for body in bodies:
            body.step(bodies, screen_dims)

    screen.fill((0, 0, 0))

    if not in_play:
        for player in players:
            if player not in bodies and player not in active_players:
                player.draw(screen, bodies)
                screen.blit(FONT.render("player {}".format(players.index(player) + 1), True, player.colour), player.defP + Vector(-7, -50))
                screen.blit(FONT.render(player.shot_type, True, player.colour), player.defP + Vector(-7, 18))

    for body in bodies:
        body.draw(screen, bodies)
    pygame.display.flip()
    clock.tick(FPS)
    frame += 1
