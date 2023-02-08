import math
import copy
import pygame
from multiprocessing import Pool

import Shot_class
import Player_class
from Vector_class import Vector

import Config as c


class Body(object):
    cmp = Vector(0, 0)
    damage_markers = list()

    def __init__(
        self, ipos=[Vector(), Vector()], imass=[0], icharge=[0], iradius=[2],
        iseparation=[0], ialignment=[0], icohesion=[0], iview_radius=[0],
        friction=0, elasticity=1, colour=((255, 255, 255), (170, 170, 170), (85, 85, 85)),
        health=None, damage=None
    ):
        """self.pos is a list of all derivatives of an object's position up to the constant term etc"""
        self.pos,         self.next_pos         = ipos,         None  # (x, dx,...)
        self.mass,        self.next_mass        = imass,        None  # (m, dm,...)
        self.charge,      self.next_charge      = icharge,      None  # (q, dq,...)
        self.radius,      self.next_radius      = iradius,      None  # (r, dr,...)
        self.cohesion,    self.next_cohesion    = icohesion,    None  # (coh, dcoh,...)
        self.alignment,   self.next_alignment   = ialignment,   None  # (ali, dali,...)
        self.separation,  self.next_separation  = iseparation,  None  # (sep, dsep,...)
        self.view_radius, self.next_view_radius = iview_radius, None  # (rad, drad,...)
        self.friction = friction  # linear friction
        self.elasticity = elasticity  # collision elasticity
        self.colour = colour  # (light, middle, dark)
        self.health = health
        self.damage = damage
        """nonzero masses have extra collision acceleration from any masses they are touching"""
        self.colliding_with = list()  # list of objects currently being collided with

    @classmethod
    def update_cmp(cls, bodies, fast=False):
        cmp = Vector(0, 0)
        if len(bodies) != 0:
            cmm = 0
            for body in bodies:
                cmp += body.mass[0] * body.pos[0]
                cmm += body.mass[0]
            if cmm > 0:
                cmp /= cmm
        if fast:
            Body.cmp = cmp
        else:
            Body.cmp = (7 * Body.cmp + cmp) / 8

    @classmethod
    def update_bodies(cls, screen, dt, bodies, presses=None):
        """
        the main function of the class to iterate through its members updating their attributes in realtime
        """
        for body in bodies:
            body.update(screen, dt, bodies, presses)

        for body in bodies:
            body.step_next()

    def update(self, screen, dt, bodies, presses):
        other_bodies = copy.copy(bodies)
        other_bodies.remove(self)
        self.set_next(screen, dt, other_bodies)

    def set_next(self, screen, dt, other_bodies):
        """
        calculates a body's attributes after a frame using its derivatives
        """
        self.next_pos = list()
        for i in range(max(len(self.pos) - 1, 2)):
            if len(self.pos) > 2 or i == 0:
                dxi = self.pos[i + 1] * dt
            else:
                dxi = Vector(0, 0)
            if i == 1:  # change in velocity
                for j, acc_func in enumerate(self.acc_funcs):
                    a = acc_func(self, other_bodies)
                    #self.draw_vector(screen, a)
                    dxi += a * dt
            self.next_pos.append(self.pos[i] + dxi)
        if len(self.pos) > 2:
            self.next_pos.append(self.pos[-1])

        self.next_mass = list()
        for i in range(len(self.mass) - 1):
            dxi = self.mass[i + 1] * dt
            self.next_mass.append(self.mass[i] + dxi)
        self.next_mass.append(self.mass[-1])

        self.next_charge = list()
        for i in range(len(self.charge) - 1):
            dxi = self.charge[i + 1] * dt
            self.next_charge.append(self.charge[i] + dxi)
        self.next_charge.append(self.charge[-1])

        self.next_radius = list()
        for i in range(len(self.radius) - 1):
            dxi = self.radius[i + 1] * dt
            self.next_radius.append(self.radius[i] + dxi)
        self.next_radius.append(self.radius[-1])

        self.next_cohesion = list()
        for i in range(len(self.cohesion) - 1):
            dxi = self.cohesion[i + 1] * dt
            self.next_cohesion.append(self.cohesion[i] + dxi)
        self.next_cohesion.append(self.cohesion[-1])

        self.next_alignment = list()
        for i in range(len(self.alignment) - 1):
            dxi = self.alignment[i + 1] * dt
            self.next_alignment.append(self.alignment[i] + dxi)
        self.next_alignment.append(self.alignment[-1])

        self.next_separation = list()
        for i in range(len(self.separation) - 1):
            dxi = self.separation[i + 1] * dt
            self.next_separation.append(self.separation[i] + dxi)
        self.next_separation.append(self.separation[-1])

    def step_next(self):
        """
        uses the calculated next attributes to shift to the next step
        """
        self.pos,        self.next_pos        = self.next_pos,        None
        self.mass,       self.next_mass       = self.next_mass,       None
        self.charge,     self.next_charge     = self.next_charge,     None
        self.radius,     self.next_radius     = self.next_radius,     None
        self.cohesion,   self.next_cohesion   = self.next_cohesion,   None
        self.alignment,  self.next_alignment  = self.next_alignment,  None
        self.separation, self.next_separation = self.next_separation, None

    def get_grav_acc(self, other_bodies):
        a = Vector(0, 0)
        for other in other_bodies:
            distance = self.pos[0].distance_to(other.pos[0])
            if distance > 0:
                direction = (other.pos[0] - self.pos[0]).normalize()
                radii = self.radius[0] + other.radius[0]
                a += direction * c.GRAV * other.mass[0] * (distance ** 2 + radii ** 4 * distance ** -2) ** -1
        return a

    def get_stat_acc(self, other_bodies):
        a = Vector(0, 0)
        if self.mass[0] != 0:
            for other in other_bodies:
                distance = self.pos[0].distance_to(other.pos[0])
                if distance > 0:
                    direction = (other.pos[0] - self.pos[0]).normalize()
                    radii = self.radius[0] + other.radius[0]
                    a += direction * c.STAT * self.charge[0] * other.charge[0] / (distance ** 2 + radii ** 4 * distance ** -2) / self.mass[0]
        return a

    def get_mag_acc(self, other_bodies):
        a = Vector(0, 0)
        if self.mass[0] != 0:
            for other in other_bodies:
                distance = self.pos[0].distance_to(other.pos[0])
                if distance > 0:
                    radius = (self.pos[0] - other.pos[0]).normalize()
                    direction = self.pos[1].rotate(c.PI / 2)
                    radii = self.radius[0] + other.radius[0]
                    axb = other.pos[1].cross(radius)
                    a += direction * c.MAG * self.charge[0] * other.charge[0] * axb / (distance ** 2 + radii ** 4 * distance ** -2) / self.mass[0]
        return a

    def get_coh_acc(self, other_bodies):
        a = Vector(0, 0)
        sum_position = sum_cohesion = 0
        for other in other_bodies:
            distance = self.pos[0].distance_to(other.pos[0])
            if distance > 0 and distance <= self.view_radius[0]:
                sum_position += other.cohesion[0] * other.pos[0]
                sum_cohesion += other.cohesion[0]
        if sum_cohesion > 0:
            a = c.COH * sum_position / sum_cohesion - self.pos[0]
        return a

    def get_ali_acc(self, other_bodies):
        a = Vector(0, 0)
        sum_velocity = sum_alignment = 0
        for other in other_bodies:
            distance = self.pos[0].distance_to(other.pos[0])
            if distance > 0 and distance <= self.view_radius[0]:
                sum_velocity += other.alignment[0] * other.pos[1]
                sum_alignment += other.alignment[0]
        if sum_alignment > 0:
            a = c.ALI * sum_velocity / sum_alignment - self.pos[1]
        return a

    def get_sep_acc(self, other_bodies):
        a = Vector(0, 0)
        for other in other_bodies:
            distance = self.pos[0].distance_to(other.pos[0])
            if distance > 0 and distance <= self.view_radius[0]:
                direction = (other.pos[0] - self.pos[0]).normalize()
                radii = self.radius[0] + other.radius[0]
                a += direction * c.SEP * self.separation[0] * other.separation[0] / distance ** 2
        return a

    def get_fric_acc(self, other_bodies):
        a = -self.pos[1] * self.friction
        return a

    def get_col_acc(self, other_bodies):
        a = Vector(0, 0)
        for other in other_bodies:
            if self.test_collision(other):
                selfpara, selfperp = self.pos[1].resolve_about(self.pos[0] - other.pos[0])
                otherpara, otherperp = other.pos[1].resolve_about(self.pos[0] - other.pos[0])
                m1, m2 = self.mass[0], other.mass[0]
                selfparanew = (m1 - m2) / (m1 + m2) * selfpara + 2 * m2 / (m1 + m2) * otherpara
                vf = selfparanew * self.elasticity + selfperp

                a += (vf - self.pos[1]) / c.DT

                if self.health is not None and other.damage is not None:
                    if isinstance(self, Player_class.Player) and isinstance(other, Player_class.Player):
                        damage = round(other.damage * (self.pos[1] - other.pos[1]).norm / 1200)
                        if other.pos[1].norm > self.pos[1].norm * 4:
                            damage *= 2
                    else:
                        damage = other.damage
                    self.health -= damage
                    if isinstance(self, Player_class.Player):
                        Body.damage_markers.append([damage, self.pos[0] - Vector(20, 20), other.colour[0], max(min(damage, 100), 30)])

        return a

    def test_collision(self, other):
        distance = self.pos[0].distance_to(other.pos[0])
        if distance > 0:
            if distance <= self.radius[0] + other.radius[0]:
                if other not in self.colliding_with:
                    self.colliding_with.append(other)
                    return True
            elif other in self.colliding_with:
                self.colliding_with.remove(other)
        return False

    acc_funcs = [
        get_grav_acc, get_stat_acc, get_mag_acc,
        get_coh_acc, get_ali_acc, get_sep_acc,
        get_fric_acc, get_col_acc
    ]

    @classmethod
    def draw_bodies(cls, screen, bodies, fixed_to_screen=False, colour=None):
        for body in bodies:
            body.draw(screen, fixed_to_screen, colour)

        if not fixed_to_screen:
            for damage_marker in cls.damage_markers:
                damage_marker[3] -= 1
                if damage_marker[3] >= 0:
                    surface = pygame.font.SysFont("Consolas", 15).render(str(damage_marker[0]), True, damage_marker[2])
                    screen.blit(surface, round(damage_marker[1] - Body.cmp + Vector(*screen.get_size()) / 2))
                else:
                    cls.damage_markers.remove(damage_marker)

    def draw(self, screen, fixed_to_screen=False, colour=None):
        if self.pos is not None:
            if colour is None:
                colour = self.colour
            if fixed_to_screen:
                P = self.pos[0]
            else:
                P = self.pos[0] - Body.cmp
            pygame.draw.circle(screen, colour[0], round(P + Vector(*screen.get_size()) / 2), round(self.radius[0]))
            if self.radius[0] >= 3:
                pygame.draw.circle(screen, colour[1], round(P + Vector(*screen.get_size()) / 2), round(self.radius[0] - 2))

    def draw_vector(self, screen, vector):
        if self.pos is not None:
            P = self.pos[0] - Body.cmp
            pygame.draw.line(screen, self.colour[1], round(P + Vector(*screen.get_size()) / 2), round(P + vector + Vector(*screen.get_size()) / 2), 2)
