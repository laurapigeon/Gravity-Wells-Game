import colorsys
import math
import random

import pygame


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
    def __init__(self, m, r, P, v=(0, 0), θ=0, ω=0, friction=(0, 0), update_type=0, player_controls=None, self_destruct=None):
        self.m = m
        self.r = r
        self.P, self.P2 = Vector(*P), None
        self.v, self.v2 = Vector(*v), None
        self.θ = θ
        self.ω = ω
        self.friction = friction
        self.update_type = update_type
        self.player_controls = player_controls
        self.self_destruct = self_destruct
        self.colour = (255, 255, 255)
        self.dark_colour = (164, 164, 164)
        self.age = 0

    def update(self, dt):
        if self.update_type:
            dPbdt1, dvbdt1, dθbdt1, dωbdt1 = self.dbdt(self.P, self.v, self.θ, self.ω)
            dP1, dv1, dθ1, dω1 = dPbdt1 * dt, dvbdt1 * dt, dθbdt1 * dt, dωbdt1 * dt
            for i in range(self.update_type - 1):
                dPbdt2, dvbdt2, dθbdt2, dωbdt2 = self.dbdt(self.P + dP1, self.v + dv1, self.θ + dθ1, self.ω + dω1)
                dP2, dv2, dθ2, dω2 = dPbdt2 * dt, dvbdt2 * dt, dθbdt2 * dt, dωbdt2 * dt
                dP1, dv1, dθ1, dω1 = (dP1 + dP2) * 0.5, (dv1 + dv2) * 0.5, (dθ1 + dθ2) * 0.5, (dω1 + dω2) * 0.5
            self.P2, self.v2, self.θ2, self.ω2 = self.P + dP1, self.v + dv1, self.θ + dθ1, self.ω + dω1

    def dbdt(self, P, v, θ, ω):
        dPbdt = v
        dvbdt = self.Σa(P, v, θ, ω)
        dθbdt = ω
        dωbdt = self.Σα(P, v, θ, ω)
        return dPbdt, dvbdt, dθbdt, dωbdt

    def Σa(self, P, v, θ, ω):
        a = Vector(0, 0)

        # friction
        a -= v * self.friction[0]

        # gravity
        for body in bodies:
            if self.P != body.P:
                s = self.P.distance_to(body.P)
                # gravacc
                #a += (body.P - self.P).normalize() * G * body.m * s ** -2

                # scaled gravacc equation to account for overlap of objects
                a += (body.P - self.P).normalize() * G * body.m * (s ** 2 + (self.r + body.r) ** 4 * s ** -2) ** -1

        # thrust
        if self.player_controls is not None:
            if keys[self.player_controls[0]]:
                a += THRUST_ACCELERATION * Vector(math.cos(θ), math.sin(θ))

        return a

    def Σα(self, P, v, θ, ω):
        α = 0

        # friction
        α -= ω * self.friction[1]

        # turning
        if self.player_controls is not None:
            if keys[self.player_controls[1]]:
                α -= TURNING_ACCELERATION
            if keys[self.player_controls[2]]:
                α += TURNING_ACCELERATION

        return α

    def step(self):
        if self.update_type:

            self.age += 1

            self.P, self.P2 = self.P2, None
            self.v, self.v2 = self.v2, None
            self.θ, self.θ2 = self.θ2, None
            self.ω, self.ω2 = self.ω2, None

            if self.self_destruct is not None:
                if self.self_destruct["t"] is not None and self.age >= self.self_destruct["t"]:
                    bodies.remove(self)
                if self.self_destruct["v"] is not None and self.v.norm() <= self.self_destruct["v"]:
                    bodies.remove(self)

    def draw(self):
        pygame.draw.circle(screen, self.colour, round(self.P), self.r)
        pygame.draw.circle(screen, self.dark_colour, round(self.P), self.r - 2)
        pygame.draw.circle(screen, self.colour, round(self.P + self.r * Vector(math.cos(self.θ), math.sin(self.θ))), round(self.r / 4))


pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)

G = 30000
THRUST_ACCELERATION = 250
TURNING_ACCELERATION = 20
BULLET_SPEED = 100

bodies = list()
bodies.append(Body(40, 20, (300, 400), (0, 0)))
bodies.append(Body(40, 20, (500, 400), (0, 0)))
bodies.append(Body(40, 20, (400, 300), (0, 0)))
bodies.append(Body(40, 20, (400, 500), (0, 0)))
bodies.append(Body(10, 20, (300, 200), (0, 0), 0, 0, (1, 2), 20, (pygame.K_e, pygame.K_s, pygame.K_f, pygame.K_SPACE)))
bodies.append(Body(10, 20, (500, 600), (0, 0), math.pi, 0, (1, 2), 20, (pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LCTRL)))

done = False
frame = 1
while not done:
    events = pygame.event.get()
    keys = pygame.key.get_pressed()
    for event in events:
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        if event.type == pygame.KEYDOWN:
            for body in bodies:
                if body.player_controls is not None:
                    if event.key == body.player_controls[3]:
                        facing = Vector(math.cos(body.θ), math.sin(body.θ))
                        P = body.P + body.r * facing
                        v = (body.v.norm() + BULLET_SPEED) * facing
                        bodies.append(Body(1, 10, P, v, 0, 0, (0.2, 0), 1, self_destruct={"t": 300, "v": 50}))

    for body in bodies:
        body.update(1 / 120)
    for body in bodies:
        body.step()

    screen.fill((0, 0, 0))
    for body in bodies:
        body.draw()
    pygame.display.flip()
    clock.tick(120)
    frame += 1
