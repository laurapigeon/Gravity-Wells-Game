import math
import pygame
import random
import colorsys


class Vector:
    def __init__(self, *args):
        """ Create a vector, example: v = Vector(1,2) """
        if len(args) == 0:
            self.values = (0, 0)
        else:
            self.values = args

    def norm(self):
        """ Returns the norm (length, magnitude) of the vector """
        return math.sqrt(sum(comp**2 for comp in self))

    def argument(self):
        """ Returns the argument of the vector, the angle clockwise from +y."""
        arg = math.acos(Vector(1, 0) * self / self.norm())
        return arg

    def distance_to(self, other):
        return (other - self).norm()

    def angle_to(self, other):
        ang = math.acos((self * other) / (self.norm() * other.norm()))
        return ang

    def normalize(self):
        """ Returns a normalized unit vector """
        norm = self.norm()
        normed = tuple(comp / norm for comp in self)
        return Vector(*normed)

    def rotate(self, *args):
        """ Rotate this vector. If passed a number, assumes this is a
            2D vector and rotates by the passed value in degrees.  Otherwise,
            assumes the passed value is a list acting as a matrix which rotates the vector.
        """
        if len(args) == 1 and isinstance(args[0], (int, float)):
            # So, if rotate is passed an int or a float...
            if len(self) != 2:
                raise ValueError("Rotation axis not defined for greater than 2D vector")
            return self._rotate2D(*args)
        elif len(args) == 1:
            matrix = args[0]
            if not all(len(row) == len(v) for row in matrix) or not len(matrix) == len(self):
                raise ValueError("Rotation matrix must be square and same dimensions as vector")
            return self.matrix_mult(matrix)

    def _rotate2D(self, theta):
        """ Rotate this vector by theta in degrees.

            Returns a new vector.
        """
        theta = math.radians(theta)
        # Just applying the 2D rotation matrix
        dc, ds = math.cos(theta), math.sin(theta)
        x, y = self.values
        x, y = dc * x - ds * y, ds * x + dc * y
        return Vector(x, y)

    def matrix_mult(self, matrix):
        """ Multiply this vector by a matrix.  Assuming matrix is a list of lists.

            Example:
            mat = [[1,2,3],[-1,0,1],[3,4,5]]
            Vector(1,2,3).matrix_mult(mat) ->  (14, 2, 26)

        """
        if not all(len(row) == len(self) for row in matrix):
            raise ValueError('Matrix must match vector dimensions')

        # Grab a row from the matrix, make it a Vector, take the dot product,
        # and store it as the first component
        product = tuple(Vector(*row) * self for row in matrix)

        return Vector(*product)

    def inner(self, other):
        """ Returns the dot product (inner product) of self and other vector
        """
        return sum(a * b for a, b in zip(self, other))

    def __mul__(self, other):
        """ Returns the dot product of self and other if multiplied
            by another Vector.  If multiplied by an int or float,
            multiplies each component by other.
        """
        if type(other) == type(self):
            return self.inner(other)
        elif isinstance(other, (int, float)):
            product = tuple(a * other for a in self)
            return Vector(*product)

    def __rmul__(self, other):
        """ Called if 4*self for instance """
        return self.__mul__(other)

    def __div__(self, other):
        if isinstance(other, (int, float)):
            divided = tuple(a / other for a in self)
            return Vector(*divided)

    def __add__(self, other):
        """ Returns the vector addition of self and other """
        added = tuple(a + b for a, b in zip(self, other))
        return Vector(*added)

    def __sub__(self, other):
        """ Returns the vector difference of self and other """
        subbed = tuple(a - b for a, b in zip(self, other))
        return Vector(*subbed)

    def __iter__(self):
        return self.values.__iter__()

    def __len__(self):
        return len(self.values)

    def __getitem__(self, key):
        return self.values[key]

    def __repr__(self):
        return str(self.values)

    def __round__(self):
        return (round(self[0]), round(self[1]))


class Body:
    def __init__(self, m, P, v, update_type=0, player_controlled=False):
        self.m = m
        self.P0, self.P, self.P2 = None, Vector(*P), None
        self.v0, self.v, self.v2 = None, Vector(*v), None

        self.update_type = update_type

    def update(self, dt):
        if self.update_type:
            dPbdt1, dvbdt1 = self.dbdt(self.P, self.v)
            dP1, dv1 = dPbdt1 * dt, dvbdt1 * dt
            for i in range(self.update_type - 1):
                dPbdt2, dvbdt2 = self.dbdt(self.P + dP1, self.v + dv1)
                dP2, dv2 = dPbdt2 * dt, dvbdt2 * dt
                dP1, dv1 = (dP1 + dP2) * 0.5, (dv1 + dv2) * 0.5
            self.P2, self.v2 = self.P + dP1, self.v + dv1

    def dbdt(self, P, v):
        dPbdt = v
        dvbdt = self.Σa(P)
        return dPbdt, dvbdt

    def Σa(self, P):
        a = Vector(0, 0)
        for body in bodies:
            if self.P != body.P:
                a += (body.P - self.P).normalize() * G * body.m * self.P.distance_to(body.P) ** -2
        return a

    def step(self):
        self.P0, self.P, self.P2 = self.P, self.P2, None
        self.v0, self.v, self.v2 = self.v, self.v2, None

    def draw(self):
        colour = tuple(round(i * 255) for i in colorsys.hsv_to_rgb((frame / 256) % 1, 1, 1))
        pygame.draw.circle(screen, colour, round(self.P), 2)


pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)

G = 30000
s1 = 15
s2 = 120
P1 = (300, 360)
P2 = (300, 360 - s1)
m1 = 100
m2 = 0.01
v1 = math.sqrt((G * m2) * (2 / s1 - 1 / s2))
v2 = math.sqrt((G * m1) * (2 / s1 - 1 / s2))

bodies = list()
bodies.append(Body(m1, P1, (0, 0), 1))
bodies.append(Body(m2, P2, (v2, 0), 5))

done = False
frame = 1
while not done:
    events = pygame.event.get()
    presses = pygame.key.get_pressed()
    for event in events:
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    for body in bodies:
        body.update(1 / 120)
    for body in bodies:
        body.step()

    #screen.fill((0, 0, 0))
    for body in bodies:
        body.draw()
    pygame.display.flip()
    clock.tick(120)
    frame += 1