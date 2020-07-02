import math


class Vector:
    def __init__(self, *args):
        if len(args) == 0:
            self.values = (0, 0)
        elif len(args) == 1 and isinstance(args[0], (list, tuple)):
            self.values = tuple(args[0])
        else:
            self.values = args

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]

    @property
    def norm(self):
        normal = math.sqrt(sum(comp**2 for comp in self))
        return normal

    @property
    def arg(self):
        argument = math.atan2(self.y, self.x)
        return argument

    def distance_to(self, other):
        length = (other - self).norm()
        return length

    def angle_to(self, other):
        angle = other.arg() - self.arg()
        return angle

    def normalize(self):
        norm = self.norm
        normed = tuple(comp / norm for comp in self)
        return Vector(*normed)

    def rotate(self, theta):
        dc, ds = math.cos(theta), math.sin(theta)
        x, y = self.values
        x, y = dc * x - ds * y, ds * x + dc * y
        return Vector(x, y)

    def inner(self, other):
        inner = sum(a * b for a, b in zip(self, other))
        return inner

    def dot(self, other):
        return self.inner(other)

    def triple(self, other):
        triple = math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.x * other.y - self.y * other.x) ** 2)
        return triple

    def cross(self, other):
        return self.triple(other)

    def __mul__(self, other):
        if type(other) == type(self):
            return self.inner(other)
        elif isinstance(other, (int, float)):
            product = tuple(a * other for a in self)
            return Vector(*product)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            divided = tuple(a / other for a in self)
            return Vector(*divided)

    def __floordiv__(self, other):
        if isinstance(other, (int, float)):
            divided = tuple(a // other for a in self)
            return Vector(*divided)

    def __neg__(self):
        negated = tuple(-a for a in self)
        return Vector(*negated)

    def __add__(self, other):
        added = tuple(a + b for a, b in zip(self, other))
        return Vector(*added)

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        subbed = tuple(a - b for a, b in zip(self, other))
        return Vector(*subbed)

    def __isub__(self, other):
        return self.__sub__(other)

    def __round__(self):
        rounded = tuple(round(a) for a in self)
        return Vector(*rounded)

    def __iter__(self):
        return self.values.__iter__()

    def __len__(self):
        return len(self.values)

    def __getitem__(self, key):
        return self.values[key]

    def __repr__(self):
        return str(self.values)


if __name__ == "__main__":
    while True:
        print(eval(input("Input: ")))