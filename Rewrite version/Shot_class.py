import math
import copy
import pygame

from Vector_class import Vector
from Body_class import Body

import Config as c


class Shot(Body):
    def __init__(
        self, ipos=[Vector()], imass=[0], icharge=[0], iradius=[2],
        iseparation=[0], ialignment=[0], icohesion=[0], iview_radius=[0],
        friction=0, elasticity=1, colour=((255, 255, 255), (170, 170, 170), (85, 85, 85)),
        health=None, damage=None, duration=None
    ):
        super().__init__(ipos, imass, icharge, iradius,
                         iseparation, ialignment, icohesion, iview_radius,
                         friction, elasticity, colour,
                         health, damage)

        self.duration = duration

    def update(self, screen, dt, bodies, presses):
        Body.update(self, screen, dt, bodies, presses)
        if self.duration is not None:
            self.duration -= 1