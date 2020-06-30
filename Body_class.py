import colorsys
import math
import random
import pygame

from Vector_class import Vector


class Body:
    def __init__(self, P, θ=0, v=(0, 0), ω=0, m=0, q=0, dm=0, dq=0, r=5, friction=(0, 0), body_type=None, shot_type=None, update_type=0, threat_reqs=None, threat_to=None, damage=1, threatened_by=None, health=1, self_destruct=None, player_controls=None, colour=(255, 255, 255), dark_colour=(164, 164, 164)):
        self.defP, self.defP2 = self.P, self.P2 = Vector(*P), None
        self.defv, self.defv2 = self.v, self.v2 = Vector(*v), None
        self.defθ, self.defθ2 = self.θ, self.θ2 = θ, None
        if θ is None:
            self.defω = self.defω2 = self.ω = self.ω2 = None
        else:
            self.defω, self.defω2 = self.ω, self.ω2 = ω, None
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
        self.defdamage = self.damage = damage
        self.threat_reqs = threat_reqs
        self.threatened_by = threatened_by
        self.defhealth = self.health = health
        self.self_destruct = self_destruct
        self.stocks = (None, 3)[self.body_type == "player"]

        self.player_controls = player_controls

        self.colour = colour
        self.dark_colour = dark_colour

        self.shot_type = shot_type
        self.shot_age = 0

        self.get_bullets()

    def get_bullets(self):
        self.bullets = list()
        if self.shot_type is not None:
            facing = Vector(math.cos(self.θ), math.sin(self.θ))
            P = self.P + self.r * facing
            v = self.v + self.player_controls[4][1] * facing
            if self.shot_type == "gun":
                self.shot_cooldown = 40
                for i in range(5):
                    self.bullets.append(Body(P, θ=None, v=Vector(225, 0), m=1, r=5, friction=(1 / 2000, 0), body_type="pellet", update_type=1,
                                             threat_reqs={"t": 5}, threat_to=("player", "pellet", "shrapnel", "bullet", "blast", "mass"), damage=2,
                                             threatened_by=("player", "pellet", "shrapnel", "bullet", "blast", "sword", "mass", "star"), health=3, self_destruct={"t": 300, "s": True},
                                             colour=self.colour, dark_colour=self.dark_colour))
            elif self.shot_type == "shotgun":
                self.shot_cooldown = 120
                for i in range(7):
                    self.bullets.append(Body(P, θ=None, v=Vector(300, 0), r=3, friction=(1 / 400, 0), body_type="shrapnel", update_type=1,
                                             threat_reqs={"t": 5, "v": 20}, threat_to=("player", "pellet", "bullet", "blast", "mass"), damage=1,
                                             threatened_by=("player", "pellet", "bullet", "blast", "sword", "mass", "star"), health=1, self_destruct={"t": 100, "s": True},
                                             colour=self.colour, dark_colour=self.dark_colour))
            elif self.shot_type == "sniper":
                self.shot_cooldown = 120
                for i in range(3):
                    self.bullets.append(Body(P, θ=None, v=Vector(450, 0), m=5, dm=20, r=3, friction=(0, 0), body_type="bullet", update_type=4,
                                             threat_reqs={"t": 5}, threat_to=("player", "pellet", "shrapnel", "bullet", "blast", "mass"), damage=1,
                                             threatened_by=("player", "pellet", "shrapnel", "bullet", "blast", "sword", "mass", "star"), health=3, self_destruct={"t": 300, "s": True},
                                             colour=self.colour, dark_colour=self.dark_colour))
            elif self.shot_type == "blaster":
                self.shot_cooldown = 120
                for i in range(8):
                    self.bullets.append(Body(P, θ=None, v=Vector(300, 0), m=0.001, r=4, friction=(1 / 200, 0), body_type="blast", update_type=1,
                                             threat_reqs={"t": 20}, threat_to=("player", "pellet", "shrapnel", "bullet", "mass"), damage=2,
                                             threatened_by=("player", "pellet", "shrapnel", "bullet", "sword", "mass", "star"), health=1, self_destruct={"t": 35, "s": True},
                                             colour=self.colour, dark_colour=self.dark_colour))
            elif self.shot_type == "melee":
                self.shot_cooldown = 120
                for i in range(4):
                    self.bullets.append(Body(P, θ=None, v=Vector((i + 1) * 75, 0), m=0, r=5, friction=(0, 0), body_type="sword", update_type=1,
                                             threat_reqs={"t": 5}, threat_to=("player", "pellet", "shrapnel", "bullet", "blast", "mass"), damage=3,
                                             threatened_by=("player", "mass", "star"), health=1, self_destruct={"t": 10, "s": True},
                                             colour=self.colour, dark_colour=self.dark_colour))
            elif self.shot_type == "flamethrower":
                self.shot_cooldown = 4
                for i in range(10):
                    self.bullets.append(Body(P, θ=None, v=Vector(360, 0), m=1, q=1, r=5, friction=(1 / 120, 0), body_type="flame", update_type=1,
                                             threat_reqs={"t": 5, "v": 20}, threat_to=("player", "mass"), damage=1,
                                             threatened_by=("player", "star"), health=1, self_destruct={"t": 150, "s": True},
                                             colour=self.colour, dark_colour=self.dark_colour))
            elif self.shot_type == "gravgun":
                self.shot_cooldown = 100
                for i in range(4):
                    self.bullets.append(Body(P, θ=None, v=Vector(150, 0), dm=5, r=10, friction=(0, 0), body_type="mass", update_type=3,
                                             threat_reqs={"t": 30}, threat_to=("player", "pellet", "shrapnel", "bullet", "blast", "sword", "flame"), damage=2,
                                             threatened_by=("player", "pellet", "shrapnel", "bullet", "blast", "sword", "star"), health=5, self_destruct={"s": True},
                                             colour=self.colour, dark_colour=self.dark_colour))

    def default(self, parent=None, factor=None):
        if self.stocks is not None:
            self.stocks -= 1
            if self.stocks < 0:
                return False

        if self.body_type in ("pellet", "bullet", "mass"):
            facing = Vector(math.cos(parent.θ), math.sin(parent.θ))
            self.P, self.P2 = parent.P + parent.r * facing, None
            self.v, self.v2 = (0.7, 0.5, 1)[("pellet", "bullet", "mass").index(self.body_type)] * parent.v + self.defv.rotate(parent.θ) * parent.player_controls[4][1] + parent.ω * parent.r * facing.rotate(math.pi / 2), None
        elif self.body_type in ("shrapnel", "flame"):
            Δθ = (math.pi / 12, math.pi / 24)[self.body_type == "flame"]
            θ = random.uniform(-Δθ, Δθ)
            facing = Vector(math.cos(parent.θ + θ), math.sin(parent.θ + θ))
            self.P, self.P2 = parent.P + parent.r * facing, None
            Δv = (0.25, 0.1)[self.body_type == "flame"]
            v = random.uniform(1 - Δv, 1 + Δv)
            if self.body_type == "flame" and parent.v.norm() != 0 and abs(parent.v.angle_to(facing)) < math.pi / 2:
                self.v, self.v2 = v * (1.6 * parent.v + self.defv.rotate(parent.θ + θ) * parent.player_controls[4][1]) + parent.ω * parent.r * facing.rotate(math.pi / 2), None
            else:
                self.v, self.v2 = v * (parent.v + self.defv.rotate(parent.θ + θ) * parent.player_controls[4][1]) + parent.ω * parent.r * facing.rotate(math.pi / 2), None
        elif self.body_type in ("blast"):
            if factor == 0:
                facing = Vector(math.cos(parent.θ), math.sin(parent.θ))
                self.P, self.P2 = parent.P + parent.r * facing, None
                self.v, self.v2 = parent.v + self.defv.rotate(parent.θ) * parent.player_controls[4][1] + parent.ω * parent.r * facing.rotate(math.pi / 2), None
            else:
                Δθ, Δv = 0.05 * math.cos(2 * math.pi * (factor - 1) / 7), 0.05 * math.sin(2 * math.pi * (factor - 1) / 7) + 1
                θ = parent.θ + Δθ
                facing = Vector(math.cos(θ), math.sin(θ))
                self.P, self.P2 = parent.P + parent.r * facing, None
                self.v, self.v2 = parent.v + Δv * self.defv.rotate(θ) * parent.player_controls[4][1] + parent.ω * parent.r * facing.rotate(math.pi / 2), None
        elif self.body_type in ("sword"):
            facing = Vector(math.cos(parent.θ), math.sin(parent.θ))
            self.P, self.P2 = parent.P + parent.r * facing, None
            if parent.v.norm() != 0 and abs(parent.v.angle_to(facing)) < math.pi / 4:
                self.v, self.v2 = 1.5 * parent.v + self.defv.rotate(parent.θ) * parent.player_controls[4][1] + parent.ω * parent.r * facing.rotate(math.pi / 2), None
            else:
                self.v, self.v2 = parent.v + self.defv.rotate(parent.θ) * parent.player_controls[4][1] + parent.ω * parent.r * facing.rotate(math.pi / 2), None
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

        self.damage = self.defdamage
        self.health = self.defhealth

        self.age = 0
        self.shot_age = 0

        self.get_bullets()

        return True

    def update(self, dt, bodies, G, Q, keys):
        if self.update_type:
            dPbdt1, dvbdt1, dθbdt1, dωbdt1, dmbdt1, ddmbdt1, dqbdt1, ddqbdt1 = self.dbdt(self.P, self.v, self.θ, self.ω, self.m, self.dm, self.q, self.dq, bodies, G, Q, keys)
            dP1, dv1, dm1, ddm1, dq1, ddq1 = dPbdt1 * dt, dvbdt1 * dt, dmbdt1 * dt, ddmbdt1 * dt, dqbdt1 * dt, ddqbdt1 * dt
            if self.θ is not None:
                dθ1, dω1 = dθbdt1 * dt, dωbdt1 * dt
            for i in range(self.update_type - 1):
                if self.θ is not None:
                    θ2, ω2 = self.θ + dθ1, self.ω + dω1
                else:
                    θ2 = ω2 = 0
                dPbdt2, dvbdt2, dθbdt2, dωbdt2, dmbdt2, ddmbdt2, dqbdt2, ddqbdt2 = self.dbdt(self.P + dP1, self.v + dv1, θ2, ω2, self.m + dm1, self.dm + ddm1, self.q + dq1, self.dq + ddq1, bodies, G, Q, keys)
                dP2, dv2, dm2, ddm2, dq2, ddq2 = dPbdt2 * dt, dvbdt2 * dt, dmbdt2 * dt, ddmbdt2 * dt, dqbdt2 * dt, ddqbdt2 * dt
                if self.θ is not None:
                    dθ2, dω2 = dθbdt2 * dt, dωbdt2 * dt
                else:
                    dθ2 = dω2 = 0
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
        if self.body_type == "blast" and self.age in (20, 21):
            dqbdt = -1
        else:
            dqbdt = dq
        ddmbdt = 0
        ddqbdt = 0
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

        # gravity and electroblast
        for body in bodies:
            if (self.P - body.P).norm() != 0:
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

        if self.body_type in ("bullet", "mass"):
            for body in bodies:
                if body.body_type == "player" and abs(self.v.angle_to(body.P - self.P)) <= math.pi / (12, 4)[self.body_type == "mass"]:
                    v = self.v.normalize()
                    s = (body.P - self.P).normalize()
                    ca = v.inner(s)
                    Δa = math.sqrt(1 - ca ** 2)
                    a += (Δa + 0.5) * self.v.norm() * (1 / (450, 150)[self.body_type == "mass"]) * self.v.rotate((-1, 1)[self.v.angle_to(body.P - self.P) > 0] * math.pi / 2)

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

    def step(self, bodies, screen_dims, frame, damage_markers):
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

            if self.body_type == "bullet" and (self.age == 15 or self.age == 30 or self.age == 60):
                self.damage += 1

            if self.body_type == "mass" and self.age == 120:
                self.damage += 1

            if self.body_type == "flame":
                if self.v.norm() <= 40:
                    self.r = 3
                elif self.v.norm() <= 120:
                    self.r = 4
                else:
                    self.r = 5

            if self.body_type == "mass" and self.age == 30:
                self.m = 30

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
            self.test_collision(body, bodies, frame, damage_markers)

    def test_collision(self, body, bodies, frame, damage_markers):
        if self != body and self.P.distance_to(body.P) <= self.r + body.r - 4 and body.threat_to is not None and self.threatened_by is not None:
            self_dangerous = self.threat_reqs is None or (("t" not in self.threat_reqs or self.age >= self.threat_reqs["t"]) and ("v" not in self.threat_reqs or self.v.norm() >= self.threat_reqs["v"]))
            body_dangerous = body.threat_reqs is None or (("t" not in body.threat_reqs or body.age >= body.threat_reqs["t"]) and ("v" not in body.threat_reqs or body.v.norm() >= body.threat_reqs["v"]))
            if self_dangerous and body_dangerous:
                if self.body_type in body.threat_to and body.body_type in self.threatened_by:
                    self.health -= body.damage
                    if self.body_type == "player":
                        damage_markers.append((body.damage, self.P - Vector(20, 20), body.colour, frame))
                if body.body_type in self.threat_to and self.body_type in body.threatened_by:
                    body.health -= self.damage
                    if body.body_type == "player":
                        damage_markers.append((self.damage, body.P - Vector(20, 20), self.colour, frame))

            if self.health <= 0 and (body.health > 0 or body.body_type != "player") and self in bodies:
                bodies.remove(self)
                # if not (body.health <= 0 and (self.health > 0 or self.body_type != "player")) and body.m != 0:
                #     body.v += self.v * self.m * (1 / body.m)
            if body.health <= 0 and (self.health > 0 or self.body_type != "player") and body in bodies:
                bodies.remove(body)
                # if not (self.health <= 0 and (body.health > 0 or body.body_type != "player")) and self.m != 0:
                #     self.v += body.v * math.log(body.m * (1 / self.m))

    def fire(self, bodies):
        if self.threat_reqs is None or self.age >= self.threat_reqs["t"]:
            self.shot_age = self.age
            if self.shot_type in ("gun", "sniper", "flamethrower", "gravgun"):
                for bullet in self.bullets:
                    if bullet not in bodies:
                        bullet.default(self)
                        bodies.append(bullet)
                        break
            elif self.shot_type in ("shotgun", "blaster", "melee"):
                for i, bullet in enumerate(self.bullets):
                    if bullet not in bodies:
                        bullet.default(self, i)
                        bodies.append(bullet)

    def draw(self, screen, bodies, players):
        self_dangerous = self.threat_reqs is None or (("t" not in self.threat_reqs or self.age >= self.threat_reqs["t"]) and ("v" not in self.threat_reqs or self.v.norm() >= self.threat_reqs["v"]))
        if not self_dangerous and self.age != 0:
            colour = self.dark_colour
            dark_colour = (64, 64, 64)
        else:
            colour = self.colour
            dark_colour = self.dark_colour
        pygame.draw.circle(screen, colour, round(self.P), self.r)
        has_bullets = False
        for bullet in self.bullets:
            has_bullets = has_bullets or bullet not in bodies
        if self.body_type != "player" or (self.age - self.shot_age) < self.shot_cooldown or not has_bullets or not self_dangerous:
            pygame.draw.circle(screen, dark_colour, round(self.P), self.r - 2)
        if self.body_type == "player":
            if self.shot_type in ("melee", "flamethrower") and self.v.norm() != 0:
                angle = (math.pi / 2, math.pi / 4)[self.shot_type == "melee"]
                pygame.draw.circle(screen, dark_colour, round(self.P + self.r * self.v.normalize().rotate(angle)), round(self.r / 3))
                pygame.draw.circle(screen, dark_colour, round(self.P + self.r * self.v.normalize().rotate(-angle)), round(self.r / 3))
            if self.shot_type in ("sniper"):
                facing = Vector(math.cos(self.θ), math.sin(self.θ))
                P = self.P + self.r * facing
                v = 0.7 * self.v + 450 * self.player_controls[4][1] * facing + self.ω * self.r * facing.rotate(math.pi / 2)
                pygame.draw.circle(screen, dark_colour, round(P + v * (1 / 20)), round(self.r / 3))
        if self.θ is not None:
            pygame.draw.circle(screen, colour, round(self.P + self.r * Vector(math.cos(self.θ), math.sin(self.θ))), round(self.r / 3))
        if self.body_type == "player":
            for i in range(self.stocks + 1):
                pygame.draw.circle(screen, colour, round(self.defP + i * Vector(20, 0) + Vector(-30, -15) + (-1, 1)[players.index(self) in (1, 2)] * Vector(50, 0)), 6)
            for i in range(self.health):
                pygame.draw.circle(screen, colour, round(self.defP + i * Vector(10, 0) + Vector(-30, 0) + (-1, 1)[players.index(self) in (1, 2)] * Vector(50, 0)), 4)
            if self.shot_type not in ("shotgun", "blaster", "melee"):
                for i, bullet in enumerate(self.bullets):
                    if bullet not in bodies:
                        pygame.draw.circle(screen, colour, round(self.defP + i * Vector(8, 0) + Vector(-30, 12) + (-1, 1)[players.index(self) in (1, 2)] * Vector(50, 0)), 2)
