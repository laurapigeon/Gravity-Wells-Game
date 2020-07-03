import math
import copy
import pygame

from Vector_class import Vector

import Config as c


class Body(object):
    update_iterations = 2

    def __init__(
        self, ipos=[Vector()], imass=[0], icharge=[0], iradius=[2],
        iseparation=[0], ialignment=[0], icohesion=[0], iview_radius=[0],
        friction=0, elasticity=0, colour=((255, 255, 255), (170, 170, 170), (85, 85, 85))
    ):
        self.prev_pos,         self.pos,         self.next_pos         = None, ipos,         None  # (x, dx,...)
        self.prev_mass,        self.mass,        self.next_mass        = None, imass,        None  # (m, dm,...)
        self.prev_charge,      self.charge,      self.next_charge      = None, icharge,      None  # (q, dq,...)
        self.prev_radius,      self.radius,      self.next_radius      = None, iradius,      None  # (r, dr,...)
        self.prev_cohesion,    self.cohesion,    self.next_cohesion    = None, icohesion,    None  # (coh, dcoh,...)
        self.prev_alignment,   self.alignment,   self.next_alignment   = None, ialignment,   None  # (ali, dali,...)
        self.prev_separation,  self.separation,  self.next_separation  = None, iseparation,  None  # (sep, dsep,...)
        self.prev_view_radius, self.view_radius, self.next_view_radius = None, iview_radius, None  # (rad, drad,...)
        self.friction                                                        = friction            # linear friction
        self.elasticity                                                      = elasticity          # collision elasticity
        self.colour                                                          = colour              # (light, middle, dark)
        self.colliding_with = list()  # list of objects currently being collided with

    @classmethod
    def update_bodies(cls, screen, dt, bodies):
        for i in range(cls.update_iterations):
            for body in bodies:
                other_bodies = copy.copy(bodies)
                other_bodies.remove(body)
                body.set_next(screen, dt, other_bodies)
            for body in bodies:
                if i == 0:
                    body.step_next()
                else:
                    body.average_next()
                body.draw_vector(screen, body.pos[1])
    """
    y -> dy -> y + dy = y2 -> dy2 -> (dy + dy2) / 2 = better dy -> y + dy = better y2 (VALID)
    y -> dy -> y + dy = y2 -> dy2 -> y2 + dy2 = y3 -> (y2 + y3) / 2 = better y2 (NOT VALID)
    (y3 - y) / 2 = better dy -> y + dy = better y2 = (y + y3) / 2
    """
    def set_next(self, screen, dt, other_bodies):
        self.next_pos = list()
        for i in range(max(len(self.pos) - 1, 2)):
            if len(self.pos) > 2 or i == 0:
                dxi = self.pos[i + 1] * dt
            else:
                dxi = Vector(0, 0)
            if i == 1:  # change in velocity
                for acc_func in self.acc_funcs:
                    # self.draw_vector(screen, acc_func(self, other_bodies))
                    dxi += acc_func(self, other_bodies) * dt
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
        self.prev_pos,        self.pos,        self.next_pos        = self.pos,        self.next_pos,        None
        self.prev_mass,       self.mass,       self.next_mass       = self.mass,       self.next_mass,       None
        self.prev_charge,     self.charge,     self.next_charge     = self.charge,     self.next_charge,     None
        self.prev_radius,     self.radius,     self.next_radius     = self.radius,     self.next_radius,     None
        self.prev_cohesion,   self.cohesion,   self.next_cohesion   = self.cohesion,   self.next_cohesion,   None
        self.prev_alignment,  self.alignment,  self.next_alignment  = self.alignment,  self.next_alignment,  None
        self.prev_separation, self.separation, self.next_separation = self.separation, self.next_separation, None

    def average_next(self):
        self.prev_pos,        self.pos,        self.next_pos        = self.pos,        list((a + b) / 2 for a, b in zip(self.prev_pos, self.next_pos)),               None
        self.prev_mass,       self.mass,       self.next_mass       = self.mass,       list((a + b) / 2 for a, b in zip(self.prev_mass, self.next_mass)),             None
        self.prev_charge,     self.charge,     self.next_charge     = self.charge,     list((a + b) / 2 for a, b in zip(self.prev_charge, self.next_charge)),         None
        self.prev_radius,     self.radius,     self.next_radius     = self.radius,     list((a + b) / 2 for a, b in zip(self.prev_radius, self.next_radius)),         None
        self.prev_cohesion,   self.cohesion,   self.next_cohesion   = self.cohesion,   list((a + b) / 2 for a, b in zip(self.prev_cohesion, self.next_cohesion)),     None
        self.prev_alignment,  self.alignment,  self.next_alignment  = self.alignment,  list((a + b) / 2 for a, b in zip(self.prev_alignment, self.next_alignment)),   None
        self.prev_separation, self.separation, self.next_separation = self.separation, list((a + b) / 2 for a, b in zip(self.prev_separation, self.next_separation)), None

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
        if self.mass[0] != 0:
            for other in other_bodies:
                if self.test_collision(other):
                    a += self.elasticity * other.mass * other.pos[1] / c.DT / self.mass
        return a

    def test_collision(self, other):
        if self.pos[0].distance_to(other.pos[0]) <= self.radius[0] + other.radius[0]:
            if other not in self.colliding_with:
                self.colliding_with.append(other)
                return True
        elif other in self.colliding_with:
            self.colliding_with.remove(other)
        return False

    acc_funcs = (
        get_grav_acc, get_stat_acc, get_mag_acc,
        get_coh_acc, get_ali_acc, get_sep_acc,
        get_fric_acc, get_col_acc
    )

    @classmethod
    def draw_bodies(cls, screen, bodies):
        for body in bodies:
            body.draw(screen)

    def draw(self, screen):
        pygame.draw.circle(screen, self.colour[0], round(self.pos[0]), round(self.radius[0]))
        if self.radius[0] >= 3:
            pygame.draw.circle(screen, self.colour[1], round(self.pos[0]), round(self.radius[0] - 2))

    def draw_vector(self, screen, vector):
        pygame.draw.line(screen, self.colour[1], round(self.pos[0]), round(self.pos[0] + vector), 2)
