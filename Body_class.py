import colorsys
import math
import random
import pygame

from Vector_class import Vector


class Body:
    def __init__(self, P, θ=0, v=(0, 0), ω=0, m=0, r=5, friction=(0, 0), body_type=None, update_type=0, threat_to=None, threat_reqs=None, threatened_by=None, player_controls=None, self_destruct=None):
        self.defP, self.defP2 = self.P, self.P2 = Vector(*P), None
        self.defv, self.defv2 = self.v, self.v2 = Vector(*v), None
        self.defθ, self.defθ2 = self.θ, self.θ2 = θ, None
        if θ is None:
            self.defω = self.defω2 = self.ω = self.ω2 = None
        else:
            self.defω, self.defω2 = ω, None
        self.defm = self.m = m
        self.defr = self.r = r
        self.defage = self.age = 0

        self.friction = friction
        self.body_type = body_type
        self.update_type = update_type
        self.threat_to = threat_to
        self.threat_reqs = threat_reqs
        self.threatened_by = threatened_by
        self.player_controls = player_controls
        self.self_destruct = self_destruct
        self.colour = (255, 255, 255)
        self.dark_colour = (164, 164, 164)

    def default(self):
        self.P = self.defP
        self.P2 = self.defP2
        self.v = self.defv
        self.v2 = self.defv2
        self.θ = self.defθ
        self.θ2 = self.defθ2
        self.ω = self.defω
        self.ω2 = self.defω2
        self.m = self.defm
        self.r = self.defr
        self.age = self.defage

    def update(self, dt, bodies, G, keys):
        if self.update_type:
            dPbdt1, dvbdt1, dθbdt1, dωbdt1 = self.dbdt(self.P, self.v, self.θ, self.ω, bodies, G, keys)
            dP1, dv1 = dPbdt1 * dt, dvbdt1 * dt
            if self.θ is not None:
                dθ1, dω1 = dθbdt1 * dt, dωbdt1 * dt
            for i in range(self.update_type - 1):
                dPbdt2, dvbdt2, dθbdt2, dωbdt2 = self.dbdt(self.P + dP1, self.v + dv1, self.θ + dθ1, self.ω + dω1, bodies, G, keys)
                dP2, dv2 = dPbdt2 * dt, dvbdt2 * dt
                if self.θ is not None:
                    dθ2, dω2 = dθbdt2 * dt, dωbdt2 * dt
                dP1, dv1 = (dP1 + dP2) * 0.5, (dv1 + dv2) * 0.5
                if self.θ is not None:
                    dθ1, dω1 = (dθ1 + dθ2) * 0.5, (dω1 + dω2) * 0.5
            self.P2, self.v2 = self.P + dP1, self.v + dv1
            if self.θ is not None:
                self.θ2, self.ω2 = self.θ + dθ1, self.ω + dω1

    def dbdt(self, P, v, θ, ω, bodies, G, keys):
        dPbdt = v
        dvbdt = self.Σa(P, v, θ, ω, bodies, G, keys)
        if θ is not None:
            dθbdt = ω
            dωbdt = self.Σα(P, v, θ, ω, bodies, G, keys)
        else:
            dθbdt = None
            dωbdt = None
        return dPbdt, dvbdt, dθbdt, dωbdt

    def Σa(self, P, v, θ, ω, bodies, G, keys):
        a = Vector(0, 0)

        # friction
        min_distance = 100000000000000
        for body in bodies:
            if body.body_type == "star":
                current_distance = self.P.distance_to(body.P) - self.r - body.r + 2
                if current_distance < min_distance:
                    min_distance = current_distance

        a -= v * self.friction[0] * min_distance

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
            if keys[self.player_controls[2][0]]:
                a += self.player_controls[2][1] * Vector(math.cos(θ), math.sin(θ))

            if keys[self.player_controls[0][0]]:
                a += self.player_controls[0][1] * Vector(math.cos(θ), math.sin(θ))

        return a

    def Σα(self, P, v, θ, ω, bodies, G, keys):
        α = 0

        # friction
        α -= ω * self.friction[1]

        # turning
        if self.player_controls is not None:
            if keys[self.player_controls[1][0]]:
                α += self.player_controls[1][1]
            if keys[self.player_controls[3][0]]:
                α += self.player_controls[3][1]

        return α

    def step(self, bodies):
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

        for body in bodies:
            if self != body and self.P.distance_to(body.P) <= self.r + body.r - 4:
                if body.threat_to is not None and self.threatened_by is not None:
                    if self.body_type in body.threat_to and body.body_type in self.threatened_by:
                        if body.body_type in self.threat_to and self.body_type in body.threatened_by:
                            if self.threat_reqs is not None:
                                if self.threat_reqs["t"] is not None and self.age >= self.threat_reqs["t"]:
                                    bodies.remove(body)
                            else:
                                bodies.remove(body)
                        if body.threat_reqs is not None:
                            if body.threat_reqs["t"] is not None and body.age >= body.threat_reqs["t"]:
                                bodies.remove(self)
                        else:
                            bodies.remove(self)

    def fire(self, bodies):
        facing = Vector(math.cos(self.θ), math.sin(self.θ))
        P = self.P + self.r * facing
        v = 0.5 * self.v + self.player_controls[4][1] * facing
        bodies.append(Body(P, θ=None, v=v, m=1, r=5, friction=(0, 0), body_type="bullet", update_type=1,
                           threat_to=("player", "bullet"), threat_reqs={"t": 10}, threatened_by=("star", "bullet"), self_destruct={"t": 300, "v": 20}))

    def draw(self, screen):
        pygame.draw.circle(screen, self.colour, round(self.P), self.r)
        pygame.draw.circle(screen, self.dark_colour, round(self.P), self.r - 2)
        if self.θ is not None:
            pygame.draw.circle(screen, self.colour, round(self.P + self.r * Vector(math.cos(self.θ), math.sin(self.θ))), round(self.r / 4))
