import math
import pygame
import random

from Player_class import Player
from Body_class import Body
from Shot_class import Shot
from Vector_class import Vector

import Config as c

pygame.init()

#screen_size = (1280, 720)
#screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)

screen_size = (1920, 1080)
screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
pygame.mouse.set_visible(False)

clock = pygame.time.Clock()


def load_sim():
    global screen_size
    bodies = list()

    colours = [
        ((164, 164, 255), (73, 73, 164)), ((164, 210, 255), (73, 119, 164)), ((164, 255, 255), (73, 164, 164)), ((164, 255, 210), (73, 164, 119)),
        ((164, 255, 164), (73, 164, 73)), ((210, 255, 164), (119, 164, 73)), ((255, 255, 164), (164, 164, 73)), ((255, 210, 164), (164, 119, 73)),
        ((255, 164, 164), (164, 73, 73)), ((255, 164, 210), (164, 73, 119)), ((255, 164, 255), (164, 73, 164)), ((210, 164, 255), (119, 73, 164))
    ]
    random.shuffle(colours)

    #                    Thrust              Left                  Reverse                Right                 Fire
    controls1 = ((pygame.K_w,  250), (pygame.K_a,    -30), (pygame.K_s,    -100), (pygame.K_d,     30), (pygame.K_z,     1))
    controls2 = ((pygame.K_UP, 250), (pygame.K_LEFT, -30), (pygame.K_DOWN, -100), (pygame.K_RIGHT, 30), (pygame.K_RCTRL, 1))
    controls3 = ((pygame.K_i,  250), (pygame.K_j,    -30), (pygame.K_k,    -100), (pygame.K_l,     30), (pygame.K_n,     1))
    controls4 = ((pygame.K_t,  250), (pygame.K_f,    -30), (pygame.K_g,    -100), (pygame.K_h,     30), (pygame.K_c,     1))

    pos1 = Vector(-screen_size[0] / 2 + 200, -screen_size[1] / 2 + 200)
    pos2 = Vector(screen_size[0] / 2 - 200, screen_size[1] / 2 - 200)
    pos3 = Vector(screen_size[0] / 2 - 200, -screen_size[1] / 2 + 200)
    pos4 = Vector(-screen_size[0] / 2 + 200, screen_size[1] / 2 - 200)

    player1 = Player(ipos=[pos1, Vector(0, 0)], imass=[1], iradius=[10], irot=[0, 0], friction=1 / 500,
                     rotfriction=5, controls=controls1, colour=colours[0], shot_type=0, health=100, damage=50, stocks=2)
    player2 = Player(ipos=[pos2, Vector(0, 0)], imass=[1], iradius=[10], irot=[c.PI, 0], friction=1 / 500,
                     rotfriction=5, controls=controls2, colour=colours[1], shot_type=1, health=100, damage=50, stocks=2)
    player3 = Player(ipos=[pos3, Vector(0, 0)], imass=[1], iradius=[10], irot=[c.PI, 0], friction=1 / 500,
                     rotfriction=5, controls=controls3, colour=colours[2], shot_type=1, health=100, damage=50, stocks=2)
    player4 = Player(ipos=[pos4, Vector(0, 0)], imass=[1], iradius=[10], irot=[0, 0], friction=1 / 500,
                     rotfriction=5, controls=controls4, colour=colours[3], shot_type=1, health=100, damage=50, stocks=2)

    players = list()
    players.append(player1)
    players.append(player2)
    players.append(player3)
    players.append(player4)

    m1 = 160 + random.random() * 80
    m2 = 160 - random.random() * 80
    r = screen_size[1] / 2
    order = 2 * random.randint(0, 1) - 1
    r1 = -order * r * m2 / (m1 + m2)
    r2 = order * r * m1 / (m1 + m2)
    P1 = Vector(r1, 0)
    P2 = Vector(r2, 0)
    v1 = math.sqrt(abs(c.GRAV * m2 * r1)) / (r1 - r2) + order * random.random() * 20
    v2 = -math.sqrt(abs(c.GRAV * m1 * r2)) / (r1 - r2) - order * random.random() * 20

    bodies.append(Body(ipos=[P1, Vector(0, v1)], imass=[m1], iradius=[m1 / 4], friction=1 / 500, colour=colours[4], damage=999))
    bodies.append(Body(ipos=[P2, Vector(0, v2)], imass=[m2], iradius=[m2 / 4], friction=1 / 500, colour=colours[5], damage=999))

    Body.update_cmp(bodies, fast=True)

    Body.update_bodies(screen, c.DT, bodies)

    return players, bodies


players, bodies = load_sim()

done = False
frame = 0
in_play = False
damage_markers = list()
active_players = 0

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
            if event.key == pygame.K_SPACE and not in_play and active_players >= 2:
                in_play = True
                for player in players:
                    if player in bodies:
                        player.default()
                for body in bodies:
                    if body in players:
                        player.default()
                    if isinstance(body, Shot):
                        bodies.remove(body)
            if event.key == pygame.K_DELETE:
                in_play = False
                for player in players:
                    if player in bodies:
                        bodies.remove(player)
                winner = None
                active_players = 0
            if event.key == pygame.K_r:
                in_play = False
                players, bodies = load_sim()
            for player in players:
                if player not in bodies and not in_play:
                    """
                    if event.key in (player.player_controls[1][0], player.player_controls[3][0]):
                        shot_type_index = shot_types.index(player.shot_type) + (-1, 1)[event.key == player.player_controls[3][0]]
                        shot_type_index %= len(shot_types)
                        player.shot_type = shot_types[shot_type_index]
                    """
                    if event.key == player.controls[4][0]:
                        player.default()
                        bodies.append(player)
                        active_players += 1

    screen.fill((0, 0, 0))

    Body.update_cmp(bodies)

    if in_play:
        Body.update_bodies(screen, c.DT, bodies, presses)

        for body in bodies:
            screen_pos = body.pos[0] - Body.cmp + Vector(*screen.get_size()) / 2
            offscreen = (screen_pos.x <= -body.radius[0] or screen_pos.x >= screen.get_width() + body.radius[0] or screen_pos.y <= -body.radius[0] or screen_pos.y >= screen.get_height() + body.radius[0])
            if (body.health is not None and body.health <= 0) or offscreen:
                if isinstance(body, Player):
                    if body.die(screen):
                        bodies.remove(body)
                        active_players -= 1
                        if active_players == 1:
                            in_play = False
                else:
                    bodies.remove(body)
            if isinstance(body, Shot) and body.duration is not None and body.duration <= 0:
                bodies.remove(body)
            # body.step_next()

    Body.draw_bodies(screen, bodies)

    if not in_play:
        for player in players:
            if player not in bodies:
                if player.pos == player.ipos:
                    player.draw(screen, fixed_to_screen=True, colour=((255, 255, 255), (164, 164, 164)))
                else:
                    player.draw(screen, fixed_to_screen=False)

    pygame.display.flip()
    clock.tick(1 / c.DT)
    frame += 1
