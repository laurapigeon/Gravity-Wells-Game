import math
import copy
import pygame
import random

from Vector_class import Vector
from Shot_class import Shot
from Body_class import Body

import Config as c


class Player(Body):
    def __init__(
        self, ipos=[Vector()], imass=[0], icharge=[0], iradius=[2],
        iseparation=[0], ialignment=[0], icohesion=[0], iview_radius=[0],
        friction=0, elasticity=1, irot=[0, 0],
        colour=((255, 255, 255), (170, 170, 170), (85, 85, 85)),
        rotfriction=0, controls=None, shot_type=0,
        health=None, damage=None, stocks=None
    ):

        self.ipos           = ipos
        self.imass          = imass
        self.icharge        = icharge
        self.iradius        = iradius
        self.icohesion      = icohesion
        self.ialignment     = ialignment
        self.iseparation    = iseparation
        self.iview_radius   = iview_radius
        self.irot           = irot
        self.ihealth        = health
        self.istocks        = stocks
        self.ishot_cooldown = (40, 120)[shot_type]

        """initiates a player body with a rotation and controls"""
        super().__init__(ipos, imass, icharge, iradius,
                         iseparation, ialignment, icohesion, iview_radius,
                         friction, elasticity, colour,
                         health, damage)

        self.thrust = 0
        self.turning = 0
        self.prev_rot, self.rot, self.next_rot = None, irot, None
        self.rotfriction = rotfriction

        self.controls = controls
        self.shot_cooldown = (40, 120)[shot_type]
        self.shot_type = shot_type
        self.stocks = stocks

    def update(self, screen, dt, bodies, presses=None):
        self.shot_cooldown -= 1
        if self.controls is not None and presses is not None:
            self.thrust = presses[self.controls[0][0]] - presses[self.controls[2][0]]
            self.turning = presses[self.controls[1][0]] - presses[self.controls[3][0]]
            if self.shot_cooldown <= 0 and presses[self.controls[4][0]]:
                Player.shoot_funcs[self.shot_type](self, bodies)

        Body.update(self, screen, dt, bodies, presses)

    def shoot_gun(self, bodies):
        shotpos = copy.copy(self.pos)
        shotvel = 225
        shotdir = self.rot[0]
        shotpos[0] += Vector(math.cos(shotdir), math.sin(shotdir)) * self.radius[0]
        shotpos[1] += Vector(math.cos(shotdir), math.sin(shotdir)) * shotvel
        shot = Shot(ipos=shotpos, imass=[0.1], iradius=[5], friction=1 / 2000, elasticity=0.2, colour=self.colour, damage=40, health=60, duration=300)
        bodies.append(shot)
        self.pos[1] -= Vector(math.cos(shotdir), math.sin(shotdir)) * shotvel * shot.mass[0] / self.mass[0]
        self.colliding_with.append(shot)
        shot.colliding_with.append(self)
        self.shot_cooldown = self.ishot_cooldown

    def shoot_shotgun(self, bodies):
        shots = list()
        for i in range(7):
            shotpos = copy.copy(self.pos)
            shotvel = 300 + (2 * random.random() - 1) * 100
            shotdir = copy.copy(self.rot[0]) + (2 * random.random() - 1) * c.PI / 12
            shotpos[0] += Vector(math.cos(self.rot[0]), math.sin(self.rot[0])) * self.radius[0]
            shotpos[1] += Vector(math.cos(shotdir), math.sin(shotdir)) * shotvel
            shot = Shot(ipos=shotpos, imass=[0.001], iradius=[3], friction=1, elasticity=0.2, colour=self.colour, damage=20, health=20, duration=100)
            bodies.append(shot)
            self.pos[1] -= Vector(math.cos(shotdir), math.sin(shotdir)) * shotvel * shot.mass[0] / self.mass[0]
            self.colliding_with.append(shot)
            shot.colliding_with.append(self)
            shots.append(shot)

        for shot in shots:
            others = copy.copy(shots)
            others.remove(shot)
            shot.colliding_with += others

        self.shot_cooldown = self.ishot_cooldown

    shoot_funcs = [
        shoot_gun, shoot_shotgun
    ]

    def set_next(self, screen, dt, other_bodies):
        Body.set_next(self, screen, dt, other_bodies)
        self.next_rot = list()
        for i in range(max(len(self.rot) - 1, 2)):
            if len(self.rot) > 2 or i == 0:
                dxi = self.rot[i + 1] * dt
            else:
                dxi = 0
            if i == 1:  # change in velocity
                for rot_func in self.rot_funcs:
                    # self.draw_vector(screen, acc_func(self, other_bodies))
                    a = rot_func(self, other_bodies)
                    dxi += a * dt
            self.next_rot.append(self.rot[i] + dxi)
        if len(self.rot) > 2:
            self.next_rot.append(self.rot[-1])

    def step_next(self):
        Body.step_next(self)
        self.prev_rot, self.rot, self.next_rot = self.rot, self.next_rot, None

    def get_fric_acc(self, other_bodies):
        min_distance = float("inf")
        for other in other_bodies:
            if not isinstance(other, Player) and not isinstance(other, Shot):
                min_distance = min(min_distance, (self.pos[0] - other.pos[0]).norm)
        if min_distance == float("inf"):
            min_distance = 100
        a = -self.pos[1] * self.friction * min_distance
        return a

    def get_ctrl_acc(self, other_bodies):
        a = Vector(0, 0)

        if self.controls is not None:
            if self.thrust == 1:
                a += self.controls[0][1] * Vector(math.cos(self.rot[0]), math.sin(self.rot[0]))

            if self.thrust == -1:
                a += self.controls[2][1] * Vector(math.cos(self.rot[0]), math.sin(self.rot[0]))

        return a

    acc_funcs = [
        Body.get_grav_acc, Body.get_stat_acc, #Body.get_mag_acc,
        Body.get_coh_acc,  Body.get_ali_acc,  Body.get_sep_acc,
        get_fric_acc, Body.get_col_acc,  get_ctrl_acc
    ]

    def get_ctrl_rot(self, other_bodies):
        a = 0

        if self.controls is not None:
            if self.turning == 1:
                a += self.controls[1][1]

            if self.turning == -1:
                a += self.controls[3][1]

        return a

    def get_fric_rot(self, other_bodies):
        a = -self.rot[1] * self.rotfriction
        return a

    rot_funcs = [get_ctrl_rot, get_fric_rot]

    def die(self, screen):
        if self.stocks is None or self.stocks > 0:
            self.default(self.stocks)
            return False
        else:
            self.stocks -= 1
            return True

    def default(self, prev_stocks=None):
        self.pos         = self.next_pos         = copy.copy(self.ipos)
        self.mass        = self.next_mass        = copy.copy(self.imass)
        self.charge      = self.next_charge      = copy.copy(self.icharge)
        self.radius      = self.next_radius      = copy.copy(self.iradius)
        self.cohesion    = self.next_cohesion    = copy.copy(self.icohesion)
        self.alignment   = self.next_alignment   = copy.copy(self.ialignment)
        self.separation  = self.next_separation  = copy.copy(self.iseparation)
        self.view_radius = self.next_view_radius = copy.copy(self.iview_radius)
        self.rot         = self.next_rot         = copy.copy(self.irot)
        self.health = self.ihealth
        self.shot_cooldown = self.shot_cooldown

        if prev_stocks is None:
            self.stocks = self.istocks
        else:
            self.stocks = prev_stocks - 1

        self.pos[0] += Body.cmp

    def draw(self, screen, fixed_to_screen, colour=None):
        if colour is None:
            colour = self.colour
        Body.draw(self, screen, fixed_to_screen, colour)
        if self.radius[0] >= 3:
            P = self.pos[0] + self.radius[0] * Vector(math.cos(self.rot[0]), math.sin(self.rot[0]))
            if not fixed_to_screen:
                P -= Body.cmp
            pygame.draw.circle(screen, colour[1], round(P + Vector(*screen.get_size()) / 2), 3)

        if self.stocks is not None:
            for i in range(self.stocks + 1):
                pygame.draw.circle(screen, colour[0], round(self.ipos[0] + Vector(*screen.get_size()) / 2 + i * Vector(20, 0) + Vector(-30, -15)), 6)
        if self.health > 0:
            P1 = round(self.ipos[0] + Vector(*screen.get_size()) / 2 + Vector(-50, 0))
            P2 = round(self.ipos[0] + Vector(*screen.get_size()) / 2 + Vector(max(self.health, 0) - 50, 0))
            pygame.draw.line(screen, colour[1], P1, P2, 2)
