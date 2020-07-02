import math
import pygame

from Vector_class import Vector

import Config as c


class Body(object):
    update_iterations = 1

    def __init__(
        self, ipos=[Vector()], imass=[0], icharge=[0], iradius=[2],
        iseparation=[0], ialignment=[0], icohesion=[0], iview_radius=[0],
        friction=0, elasticity=0, colour=((255, 255, 255), (170, 170, 170), (85, 85, 85))
    ):
        self.pos,         self.next_pos         = ipos,         None  # (x, dx,...)
        self.mass,        self.next_mass        = imass,        None  # (m, dm,...)
        self.charge,      self.next_charge      = icharge,      None  # (q, dq,...)
        self.radius,      self.next_radius      = iradius,      None  # (r, dr,...)
        self.cohesion,    self.next_cohesion    = icohesion,    None  # (coh, dcoh,...)
        self.alignment,   self.next_alignment   = ialignment,   None  # (ali, dali,...)
        self.separation,  self.next_separation  = iseparation,  None  # (sep, dsep,...)
        self.view_radius, self.next_view_radius = iview_radius, None  # (rad, drad,...)
        self.friction                           = friction,     None  # linear friction
        self.elasticity                         = elasticity,   None  # collision elasticity
        self.colour                             = colour,       None  # (light, middle, dark)

    @classmethod
    def update_bodies(cls, dt, bodies):
        for i in range(cls.update_iterations):
            for body in bodies:
                other_bodies = bodies.remove(body)
                body.set_next(dt, other_bodies)
            for body in bodies:
                if i == 0:
                    body.step_next()
                else:
                    body.average_next()

    def set_next(self, dt, other_bodies):
        self.next_pos = list()
        for i in range(len(self.pos) - 1):
            dxi = self.pos[i + 1] * dt
            if i == 1:  # change in velocity
                dxi += sum(self.acc_func(other_bodies) * dt for acc_func in self.acc_funcs)
            self.next_pos.append(self.pos[i] + dxi)
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
        self.pos,        self.next_pos        = self.next_pos,        None
        self.mass,       self.next_mass       = self.next_mass,       None
        self.charge,     self.next_charge     = self.next_charge,     None
        self.radius,     self.next_radius     = self.next_radius,     None
        self.cohesion,   self.next_cohesion   = self.next_cohesion,   None
        self.alignment,  self.next_alignment  = self.next_alignment,  None
        self.separation, self.next_separation = self.next_separation, None

    def average_next(self):
        self.pos,        self.next_pos        = list((a + b) / 2 for a, b in zip(self.pos, self.next_pos)),               None
        self.mass,       self.next_mass       = list((a + b) / 2 for a, b in zip(self.mass, self.next_mass)),             None
        self.charge,     self.next_charge     = list((a + b) / 2 for a, b in zip(self.charge, self.next_charge)),         None
        self.radius,     self.next_radius     = list((a + b) / 2 for a, b in zip(self.radius, self.next_radius)),         None
        self.cohesion,   self.next_cohesion   = list((a + b) / 2 for a, b in zip(self.cohesion, self.next_cohesion)),     None
        self.alignment,  self.next_alignment  = list((a + b) / 2 for a, b in zip(self.alignment, self.next_alignment)),   None
        self.separation, self.next_separation = list((a + b) / 2 for a, b in zip(self.separation, self.next_separation)), None

    def get_grav_acc(self, other_bodies):
        a = 0
        for other in other_bodies:
            distance = self.pos[0].distance_to(other.pos[0])
            direction = (other.pos[0] - self.pos[0]).normalize()
            radii = self.radius[0] + other.radius[0]
            a += direction * c.GRAV * other.mass[0] / (distance ** 2 + radii ** 4 * distance ** -2)
        return a

    def get_stat_acc(self, other_bodies):
        a = 0
        if self.mass[0] != 0:
            for other in other_bodies:
                distance = self.pos[0].distance_to(other.pos[0])
                direction = (other.pos[0] - self.pos[0]).normalize()
                radii = self.radius[0] + other.radius[0]
                a += direction * c.STAT * self.charge[0] * other.charge[0] / (distance ** 2 + radii ** 4 * distance ** -2) / self.mass[0]
        return a

    def get_mag_acc(self, other_bodies):
        a = 0
        return a

    def get_coh_acc(self, other_bodies):
        a = 0
        return a

    def get_ali_acc(self, other_bodies):
        a = 0
        return a

    def get_sep_acc(self, other_bodies):
        a = 0
        if self.mass[0] != 0:
            for other in other_bodies:
                distance = self.pos[0].distance_to(other.pos[0])
                if distance <= self.view_radius[0]:
                    direction = (other.pos[0] - self.pos[0]).normalize()
                    radii = self.radius[0] + other.radius[0]
                    a += direction * c.SEP * self.separation[0] * other.separation[0] / distance ** 2 / self.mass[0]
        return a

    def get_fric_acc(self, other_bodies):
        a = -self.pos[1] * self.friction
        return a

    def get_col_acc(self, other_bodies):
        a = 0
        if self.mass[0] != 0:
            for other in other_bodies:
                if self.test_collision(other):
                    a += other.mass * other.pos[1] / c.DT / self.mass
        return a

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
