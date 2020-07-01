import math
import copy
import random
import pygame

from Body_class import Body
from Vector_class import Vector

import Config as c

import sys
import os


def resource_path(relative_path):
    try:  # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


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
damage_markers = list()
in_play = False
shot_types = ("gun", "shotgun", "sniper", "blaster", "melee", "flamethrower", "gravgun")
winner = None
wins = [0, 0, 0, 0]
player_names = ["player 1", "Gwyn", "Key", "Laura"]
colours = [
    ((164, 164, 255), (73, 73, 164)), ((164, 210, 255), (73, 119, 164)), ((164, 255, 255), (73, 164, 164)), ((164, 255, 210), (73, 164, 119)),
    ((164, 255, 164), (73, 164, 73)), ((210, 255, 164), (119, 164, 73)), ((255, 255, 164), (164, 164, 73)), ((255, 210, 164), (164, 119, 73)),
    ((255, 164, 164), (164, 73, 73)), ((255, 164, 210), (164, 73, 119)), ((255, 164, 255), (164, 73, 164)), ((210, 164, 255), (119, 73, 164))
]
random.shuffle(colours)

bodies.append(Body((int(screen_dims[0] / 2 + 300), int(screen_dims[1] / 2)), θ=None, m=160, r=40, body_type="star", threat_to=("player", "pellet", "shrapnel", "bullet", "blast", "flame", "mass"), damage=999))
bodies.append(Body((int(screen_dims[0] / 2 - 300), int(screen_dims[1] / 2)), θ=None, m=160, r=40, body_type="star", threat_to=("player", "pellet", "shrapnel", "bullet", "blast", "flame", "mass"), damage=999))
player1 = Body((200, 200), r=10, friction=(1 / 400, 5), body_type="player", shot_type="gun",
               update_type=1, threat_reqs={"t": 150}, threat_to=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass"), damage=5,
               threatened_by=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass", "star"), health=5, self_destruct={"s": True},
               player_controls=((pygame.K_w, 250), (pygame.K_a, -30), (pygame.K_s, -100), (pygame.K_d, 30), (pygame.K_LSHIFT, 1)), colour=colours[0][0], dark_colour=colours[0][1])
player2 = Body((screen_dims[0] - 200, screen_dims[1] - 200), θ=math.pi, r=10, friction=(1 / 400, 5), body_type="player", shot_type="gun",
               update_type=1, threat_reqs={"t": 150}, threat_to=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass"), damage=5,
               threatened_by=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass", "star"), health=5, self_destruct={"s": True},
               player_controls=((pygame.K_UP, 250), (pygame.K_LEFT, -30), (pygame.K_DOWN, -100), (pygame.K_RIGHT, 30), (pygame.K_RCTRL, 1)), colour=colours[1][0], dark_colour=colours[1][1])
player3 = Body((screen_dims[0] - 200, 200), θ=math.pi, r=10, friction=(1 / 400, 5), body_type="player", shot_type="gun",
               update_type=1, threat_reqs={"t": 150}, threat_to=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass"), damage=5,
               threatened_by=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass", "star"), health=5, self_destruct={"s": True},
               player_controls=((pygame.K_i, 250), (pygame.K_j, -30), (pygame.K_k, -100), (pygame.K_l, 30), (pygame.K_n, 1)), colour=colours[2][0], dark_colour=colours[2][1])
player4 = Body((200, screen_dims[1] - 200), r=10, friction=(1 / 400, 5), body_type="player", shot_type="gun",
               update_type=1, threat_reqs={"t": 150}, threat_to=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass"), damage=5,
               threatened_by=("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass", "star"), health=5, self_destruct={"s": True},
               player_controls=((pygame.K_t, 250), (pygame.K_f, -30), (pygame.K_g, -100), (pygame.K_h, 30), (pygame.K_c, 1)), colour=colours[3][0], dark_colour=colours[3][1])

players.append(player1)
players.append(player2)
players.append(player3)
players.append(player4)

done = False
frame = 1
FPS = 60
FONT = pygame.font.SysFont("Consolas", 20)
SMALL_FONT = pygame.font.SysFont("Consolas", 15)

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
            if event.key == pygame.K_SPACE and not in_play and len(active_players) >= 2:
                in_play = True
                for player in players:
                    if player not in active_players:
                        player.stocks = 3
                        player.default()
                    player.stocks = 2
                    player.health = 5
                for body in bodies:
                    if body.body_type in ("pellet", "shrapnel", "bullet", "blast", "sword", "flame", "mass"):
                        bodies.remove(body)
            if event.key == pygame.K_DELETE:
                in_play = False
                for player in active_players:
                    if player in bodies:
                        bodies.remove(player)
                winner = None
                active_players = list()
            for player in players:
                if player not in bodies and player not in active_players and not in_play:
                    if event.key in (player.player_controls[1][0], player.player_controls[3][0]):
                        shot_type_index = shot_types.index(player.shot_type) + (-1, 1)[event.key == player.player_controls[3][0]]
                        shot_type_index %= len(shot_types)
                        player.shot_type = shot_types[shot_type_index]
                    elif event.key == player.player_controls[4][0]:
                        player.stocks = 4
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
                    winner = (players.index(active_players[0]), active_players[0].colour, active_players[0].shot_type)
                    wins[winner[0]] += 1
                    active_players = list()

    if len(active_players) >= 1:
        for body in bodies:
            body.update(1 / FPS, bodies, G, Q, keys)
        for body in bodies:
            body.step(bodies, screen_dims, frame, damage_markers)

    screen.fill((0, 0, 0))

    if not in_play:
        for i, player in enumerate(players):
            if player not in bodies and player not in active_players:
                player.draw(screen, bodies, players)
                screen.blit(FONT.render(player_names[players.index(player)], True, player.colour), player.defP + Vector(-37, -50) + (-1, 1)[players.index(player) in (1, 2)] * Vector(50, 0))
                screen.blit(FONT.render(player.shot_type, True, player.colour), player.defP + Vector(-37, 18) + (-1, 1)[players.index(player) in (1, 2)] * Vector(50, 0))
                screen.blit(FONT.render("{} wins".format(wins[i]), True, player.colour), player.defP + Vector(-37, 40) + (-1, 1)[players.index(player) in (1, 2)] * Vector(50, 0))
        if winner is not None:
            surface = FONT.render("{} wins as {}!".format(player_names[winner[0]], winner[2]), True, winner[1])
            rect = (int(screen_dims[0] / 2 - surface.get_rect().w / 2), int(screen_dims[1] / 2 - surface.get_rect().h / 2))
            screen.blit(surface, rect)
        if len(active_players) >= 2:
            surface = FONT.render("[press space to start]", True, (255, 255, 255))
            rect = (int(screen_dims[0] / 2 - surface.get_rect().w / 2), int(screen_dims[1] - surface.get_rect().h / 2 - 50))
            screen.blit(surface, rect)

    for body in bodies:
        body.draw(screen, bodies, players)
    for damage_marker in damage_markers:
        if frame - damage_marker[3] <= 20 * (damage_marker[0] % 6):
            surface = SMALL_FONT.render(str(damage_marker[0]), True, damage_marker[2])
            screen.blit(surface, (int(damage_marker[1][0]), int(damage_marker[1][1])))
        else:
            damage_markers.remove(damage_marker)
    pygame.display.flip()
    clock.tick(FPS)
    frame += 1
