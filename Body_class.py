import colorsys
import math
import random
import pygame

from Vector_class import Vector


class Body:
    def __init__(self, P, θ=0, v=(0, 0), ω=0, m=0, q=0, dm=0, dq=0, r=5, friction=(0, 0), body_type=None, shot_type=None, update_type=0, threat_reqs=None, threat_to=None, damage=1, threatened_by=None, health=1, self_destruct=None, player_controls=None):
        self.defP, self.defP2 = self.P, self.P2 = Vector(*P), None
        self.defv, self.defv2 = self.v, self.v2 = Vector(*v), None
        self.defθ, self.defθ2 = self.θ, self.θ2 = θ, None
        if θ is None:
            self.defω = self.defω2 = self.ω = self.ω2 = None
        else:
            self.defω, self.defω2 = ω, None
        self.defm = self.m = m
        self.defq = self.q = q
        self.defdm = self.dm = dm
        self.defdq = self.dq = dq
        self.defr = self.r = r
        self.defage = self.age = 0

        self.friction = friction
        self.body_type = body_type
        self.update_type = update_type
        self.threat_to = threat_to
        self.damage = damage
        self.threat_reqs = threat_reqs
        self.threatened_by = threatened_by
        self.defhealth = self.health = health
        self.self_destruct = self_destruct

        self.player_controls = player_controls
        self.colour = (255, 255, 255)
        self.dark_colour = (164, 164, 164)

        self.shot_type = shot_type
        self.shot_age = 0

        self.bullets = list()
        if self.shot_type is not None:
            facing = Vector(math.cos(self.θ), math.sin(self.θ))
            P = self.P + self.r * facing
            v = self.v + self.player_controls[4][1] * facing
            if self.shot_type == "gun":
                self.shot_cooldown = 30
                for i in range(4):
                    self.bullets.append(Body(P, θ=None, v=Vector(0.75, 0), m=1, r=5, friction=(1 / 2000, 0), body_type="pellet", update_type=1,
                                             threat_reqs={"t": 10}, threat_to=("player", "pellet", "shrapnel", "bullet", "static"), damage=2,
                                             threatened_by=("player", "pellet", "shrapnel", "bullet", "static", "star"), health=2, self_destruct={"t": 300, "v": 20, "s": True}))
            elif self.shot_type == "shotgun":
                self.shot_cooldown = 90
                for i in range(6):
                    self.bullets.append(Body(P, θ=None, v=Vector(1, 0), r=3, friction=(1 / 400, 0), body_type="shrapnel", update_type=1,
                                             threat_reqs={"t": 5}, threat_to=("player", "pellet", "bullet", "static"), damage=1,
                                             threatened_by=("player", "pellet", "bullet", "static", "star"), health=1, self_destruct={"t": 100, "v": 20, "s": True}))
            elif self.shot_type == "sniper":
                self.shot_cooldown = 120
                for i in range(2):
                    self.bullets.append(Body(P, θ=None, v=Vector(1.5, 0), m=5, dm=30, r=4, friction=(0, 0), body_type="bullet", update_type=1,
                                             threat_reqs={"t": 10}, threat_to=("player", "pellet", "shrapnel", "bullet", "static"), damage=3,
                                             threatened_by=("player", "pellet", "shrapnel", "bullet", "static", "star"), health=2, self_destruct={"t": 300, "v": 20, "s": True}))
            elif self.shot_type == "science":
                self.shot_cooldown = 180
                for i in range(7):
                    self.bullets.append(Body(P, θ=None, v=Vector(0.75, 0), m=0.5, r=6, friction=(0, 0), body_type="static", update_type=1,
                                             threat_reqs={"t": 20}, threat_to=("player", "pellet", "shrapnel", "bullet"), damage=2,
                                             threatened_by=("player", "pellet", "shrapnel", "bullet", "star"), health=1, self_destruct={"t": 80, "s": True}))

    def default(self, parent=None):
        if self.body_type in ("pellet", "bullet"):
            facing = Vector(math.cos(parent.θ), math.sin(parent.θ))
            self.P, self.P2 = parent.P + parent.r * facing, None
            self.v, self.v2 = 0.5 * parent.v + self.defv.norm() * parent.player_controls[4][1] * facing, None
        elif self.body_type in ("shrapnel", "static"):
            Δθ = math.pi / (8, 512)[self.body_type == "static"]
            θ = parent.θ + random.uniform(-Δθ, Δθ)
            facing = Vector(math.cos(θ), math.sin(θ))
            self.P, self.P2 = parent.P + parent.r * facing, None
            Δv = (0.25, 0.001)[self.body_type == "static"]
            self.v, self.v2 = random.uniform(1 - Δv, 1 + Δv) * (parent.v + self.defv.norm() * parent.player_controls[4][1] * facing), None
        else:
            self.P = self.defP
            self.P2 = self.defP2
            self.v = self.defv
            self.v2 = self.defv2
        self.θ = self.defθ
        self.θ2 = self.defθ2
        self.ω = self.defω
        self.ω2 = self.defω2
        self.m = self.defm
        self.q = self.defq
        self.dm = self.defdm
        self.dq = self.defdq
        self.r = self.defr

        self.health = self.defhealth

        self.age = 0
        self.shot_age = 0

    def update(self, dt, bodies, G, Q, keys):
        if self.update_type:
            dPbdt1, dvbdt1, dθbdt1, dωbdt1, dmbdt1, ddmbdt1, dqbdt1, ddqbdt1 = self.dbdt(self.P, self.v, self.θ, self.ω, self.m, self.dm, self.q, self.dq, bodies, G, Q, keys)
            dP1, dv1, dm1, ddm1, dq1, ddq1 = dPbdt1 * dt, dvbdt1 * dt, dmbdt1 * dt, ddmbdt1 * dt, dqbdt1 * dt, ddqbdt1 * dt
            if self.θ is not None:
                dθ1, dω1 = dθbdt1 * dt, dωbdt1 * dt
            for i in range(self.update_type - 1):
                dPbdt2, dvbdt2, dθbdt2, dωbdt2, dmbdt2, ddmbdt2, dqbdt2, ddqbdt2 = self.dbdt(self.P + dP1, self.v + dv1, self.θ + dθ1, self.ω + dω1, self.m + dm, self.dm + ddm, self.q + dq, self.dq + ddq, bodies, G, Q, keys)
                dP2, dv2, dm2, ddm2, dq2, ddq2 = dPbdt2 * dt, dvbdt2 * dt, dmbdt2 * dt, ddmbdt2 * dt, dqbdt2 * dt, ddqbdt2 * dt
                if self.θ is not None:
                    dθ2, dω2 = dθbdt2 * dt, dωbdt2 * dt
                dP1, dv1, dm1, ddm1, dq1, ddq1 = (dP1 + dP2) * 0.5, (dv1 + dv2) * 0.5, (dm1 + dm2) * 0.5, (ddm1 + ddm2) * 0.5, (dq1 + dq2) * 0.5, (ddq1 + ddq2) * 0.5
                if self.θ is not None:
                    dθ1, dω1 = (dθ1 + dθ2) * 0.5, (dω1 + dω2) * 0.5
            self.P2, self.v2, self.m2, self.dm2, self.q2, self.dq2 = self.P + dP1, self.v + dv1, self.m + dm1, self.dm + ddm1, self.q + dq1, self.dq + ddq1
            if self.θ is not None:
                self.θ2, self.ω2 = self.θ + dθ1, self.ω + dω1

    def dbdt(self, P, v, θ, ω, m, dm, q, dq, bodies, G, Q, keys):
        dPbdt = v
        dvbdt = self.Σa(P, v, θ, ω, m, dm, q, dq, bodies, G, Q, keys)
        if θ is not None:
            dθbdt = ω
            dωbdt = self.Σα(P, v, θ, ω, m, dm, q, dq, bodies, G, Q, keys)
        else:
            dθbdt = None
            dωbdt = None
        dmbdt = dm
        dqbdt = dq
        ddmbdt = 0
        ddqbdt = (0, 0.5)[self.body_type == "static"] + 4 * dq
        return dPbdt, dvbdt, dθbdt, dωbdt, dmbdt, ddmbdt, dqbdt, ddqbdt

    def Σa(self, P, v, θ, ω, m, dm, q, dq, bodies, G, Q, keys):
        a = Vector(0, 0)

        # friction
        min_distance = 100000000000000
        for body in bodies:
            if body.body_type == "star":
                current_distance = self.P.distance_to(body.P) - self.r - body.r + 2
                if current_distance < min_distance:
                    min_distance = current_distance

        a -= v * self.friction[0] * min_distance

        # gravity and electrostatic
        for body in bodies:
            if self.P != body.P:
                s = self.P.distance_to(body.P)
                # gravacc
                #a += (body.P - self.P).normalize() * G * body.m * s ** -2

                # scaled gravacc equation to account for overlap of objects
                a += (body.P - self.P).normalize() * G * body.m * (s ** 2 + (self.r + body.r) ** 4 * s ** -2) ** -1

                # elecstatacc
                if m != 0:
                    a += -1 * (body.P - self.P).normalize() * Q * q * body.q * s ** -2 * m ** -1

        # thrust
        if self.player_controls is not None:
            if keys[self.player_controls[2][0]]:
                a += self.player_controls[2][1] * Vector(math.cos(θ), math.sin(θ))

            if keys[self.player_controls[0][0]]:
                a += self.player_controls[0][1] * Vector(math.cos(θ), math.sin(θ))

        return a

    def Σα(self, P, v, θ, ω, m, dm, q, dq, bodies, G, Q, keys):
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

    def step(self, bodies, screen_dims):
        if self.update_type:

            self.age += 1

            self.P, self.P2 = self.P2, None
            self.v, self.v2 = self.v2, None
            self.θ, self.θ2 = self.θ2, None
            self.ω, self.ω2 = self.ω2, None
            self.m, self.m2 = self.m2, None
            self.dm, self.dm2 = self.dm2, None
            self.q, self.q2 = self.q2, None
            self.dq, self.dq2 = self.dq2, None

            if self.self_destruct is not None:
                if "t" in self.self_destruct and self.age >= self.self_destruct["t"]:
                    bodies.remove(self)
                    return
                elif "v" in self.self_destruct and self.v.norm() <= self.self_destruct["v"]:
                    bodies.remove(self)
                    return
                elif "s" in self.self_destruct and (self.P[0] < 0 or self.P[1] < 0 or self.P[0] > screen_dims[0] or self.P[1] > screen_dims[1]):
                    bodies.remove(self)
                    return

        for body in bodies:
            if self != body and self.P.distance_to(body.P) <= self.r + body.r - 4 and body.threat_to is not None and self.threatened_by is not None:
                if (self.threat_reqs is None or self.age >= self.threat_reqs["t"]) and (body.threat_reqs is None or body.age >= body.threat_reqs["t"]):
                    if self.body_type in body.threat_to and body.body_type in self.threatened_by:
                        self.health -= body.damage
                    if body.body_type in self.threat_to and self.body_type in body.threatened_by:
                        body.health -= self.damage

                if self.health <= 0:
                    bodies.remove(self)
                if body.health <= 0:
                    bodies.remove(body)
                return

    def fire(self, bodies):
        self.shot_age = self.age
        if self.shot_type in ("gun", "sniper"):
            for bullet in self.bullets:
                if bullet not in bodies:
                    bullet.default(self)
                    bodies.append(bullet)
                    break
        elif self.shot_type in ("shotgun", "science"):
            for bullet in self.bullets:
                if bullet not in bodies:
                    bullet.default(self)
                    bodies.append(bullet)

    def draw(self, screen):
        if self.threat_reqs is None or self.age >= self.threat_reqs["t"]:
            colour = (255, 200, 200)
            dark_colour = (164, 100, 100)
        else:
            colour = (255, 255, 255)
            dark_colour = (164, 164, 164)
        pygame.draw.circle(screen, colour, round(self.P), self.r)
        pygame.draw.circle(screen, dark_colour, round(self.P), self.r - 2)
        if self.θ is not None:
            pygame.draw.circle(screen, colour, round(self.P + self.r * Vector(math.cos(self.θ), math.sin(self.θ))), round(self.r / 4))
        if self.body_type == "player":
            for i in range(self.health):
                pygame.draw.circle(screen, colour, round(self.defP + i * Vector(10, 0)), 3)
