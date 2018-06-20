
from __future__ import division

import math

EPSILON = 0.0000001

class Vec3(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def normalize(self):
        return self/self.length()

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def __add__(self, _):
        return Vec3(self.x + _.x, self.y + _.y, self.z + _.z)

    def __sub__(self, _):
        return self + -_

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    def __truediv__(self, _):
        return Vec3(self.x / _, self.y / _, self.z / _)

    def __rmul__(self, _):
        return Vec3(_ * self.x, _ * self.y, _ * self.z)

    def dot(self, _):
        return self.x * _.x + self.y * _.y + self.z * _.z

    def along_normal(self, n):
        lgt = n.length()
        return self.dot(n) * n/(lgt * lgt)

    def cross(self, _):
        return Vec3(self.y * _.z - self.z * _.y,
                    -(self.x * _.z - self.z * _.x),
                    self.x * _.y - self.y * _.x)

    __mul__ = __rmul__

    def __repr__(self):
        return "<%s, %s, %s>" % (self.x, self.y, self.z)

    def __eq__(self, _):
        return self.x == _.x and self.y == _.y and self.z == _.z

    def __ne__(self, _):
        return not self == _

class Ray(object):
    def __init__(self, A, B):
        self.A = A
        self.B = B

    def point_at_parameter(self, t):
        return self.A + t * self.B

    def __repr__(self):
        return "%r -> %r" % (self.A, self.B)

class Triangle(object):
    def __init__(self, a, b, c, material):
        self.a = a
        self.b = b
        self.c = c
        self.N = (b - a).cross(c - b).normalize()
        self.material = material

    def hit(self, r, t_min, t_max):
        a = self.a
        b = self.b
        c = self.c
        X = (a - r.A).cross(r.B)
        Y = (b - r.A).cross(r.B)
        if (X.cross(Y).dot(r.B) > 0):
            return -1
        X = (b - r.A).cross(r.B)
        Y = (c - r.A).cross(r.B)
        if (X.cross(Y).dot(r.B) > 0):
            return -1
        X = (c - r.A).cross(r.B)
        Y = (a - r.A).cross(r.B)
        if (X.cross(Y).dot(r.B) > 0):
            return -1
        B = ((-r.B).dot(self.N))
        r = (self.N.dot(r.A - self.a)) / B
        if r < t_min or r > t_max:
            return -1
        return r

    def normal(self, point):
        return self.N

class Sphere(object):
    def __init__(self, center, r, material):
        self.center = center
        self.r = r
        self.material = material

    def normal(self, point):
        return (point - self.center).normalize()

    def hit(self, r, t_min, t_max):
        oc = r.A - self.center
        a = r.B.dot(r.B)
        b = oc.dot(r.B)
        c = oc.dot(oc) - self.r * self.r
        discriminant = b * b - a * c
        if discriminant < 0:
            return -1
        r = (-b - math.sqrt(discriminant)) / a
        if r > t_min and r < t_max:
            return r
        return -1
