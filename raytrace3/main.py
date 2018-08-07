
from __future__ import division

import pygame, time, math, sys
import cffi
from random import random
from vec import Vec3, Ray, Triangle, Sphere
from mat import Material
pygame.font.init()

myfont = pygame.font.SysFont('Arial MS', 30)

pygame.init()
X = 1000
Y = 500

ffi = cffi.FFI()

screen = pygame.display.set_mode((X, Y))

class ScreenWrapper(object):
    def __init__(self, screen):
        self._screen = screen
        self._buf = ffi.cast("unsigned char *", screen._pixels_address)

    def fill(self):
        self._screen.fill(0)

    def __setitem__(self, (x, y), c):
        target = (y * X + x) * 4
        # sqrt() is for gamma correction
        self._buf[target + 2] = int(math.sqrt(c.x) * 255.99)
        self._buf[target + 1] = int(math.sqrt(c.y) * 255.99)
        self._buf[target    ] = int(math.sqrt(c.z) * 255.99)

origin = Vec3(0., 0., 0.)
vertical = Vec3(0.0, 2.0, 0.0)
horizontal = Vec3(4.0, 0.0, 0.0)
lower_left_corner = Vec3(-2.0, -1.0, -1.0)

tris = [
#    [(0, 0.8, -1), (-0.8, 0, -1), (0, 0, -0.4)]
#    [(0, 0, -1), (1, 0, -2), (0, 1, -2)],
#    [(0, 0, -1), (0, 1, -2), (-1, 0, -2)],
#    [(0, 0, -1), (-1, 0, -2), (0, -1, -2)],

     [(0.1, 0.8, -0.7), (-0.8, -0.6, -1), (-0.7, -0.6, -0.4)],
    ]

mat = Material(Vec3(0.9, 0.04, 0.04), softness=0.3)

for i in range(len(tris)):
    a, b, c = tris[i]
    tris[i] = Triangle(Vec3(*a), Vec3(*b), Vec3(*c), mat)
    tris.append(Triangle(Vec3(*a), Vec3(*c), Vec3(*b), mat))  # reversed

mat = Material(Vec3(0.56, 0.56, 0.56), mirror=0.8, softness=0.)
tris.append(Sphere(Vec3(0, 0, -1), 0.5, mat))

# rounded "floor"
mat = Material(Vec3(0.9, 0.9, 0.0))
tris.append(Sphere(Vec3(0, -100.5, -1), 100, mat))

RAYS = 5
SUN_DIRECTION = Vec3(-0.2, 1, 0.1).normalize()


# ------------------------------------------------------------------



class OcLeaf(object):
    def __init__(self, center):
        self.center = center
        self.blocked = False


class OcTree(object):
    def __init__(self, vmin, vmax, n):
        self.vmin = vmin
        self.vmax = vmax
        self.n = n
        self.leaves = {}
        self.unit = min(
            (self.vmax.x - self.vmin.x) / self.n,
            (self.vmax.y - self.vmin.y) / self.n,
            (self.vmax.z - self.vmin.z) / self.n)

    def get_leaf(self, v):
        v -= self.vmin
        ix = v.x * self.n / (self.vmax.x - self.vmin.x)
        iy = v.y * self.n / (self.vmax.y - self.vmin.y)
        iz = v.z * self.n / (self.vmax.z - self.vmin.z)
        if ix < 0.0 or iy < 0.0 or iz < 0.0:
            return None
        ix = int(ix)
        iy = int(iy)
        iz = int(iz)
        try:
            return self.leaves[ix, iy, iz]
        except KeyError:
            if ix >= self.n or iy >= self.n or iz >= self.n:
                return None
            x = (ix + 0.5) * (self.vmax.x - self.vmin.x) / self.n
            y = (iy + 0.5) * (self.vmax.y - self.vmin.y) / self.n
            z = (iz + 0.5) * (self.vmax.z - self.vmin.z) / self.n
            center = Vec3(x, y, z) + self.vmin
            leaf = OcLeaf(center)
            self.leaves[ix, iy, iz] = leaf
            assert leaf is self.get_leaf(center)
            return leaf

    def enum_centers_x(self):
        return [self.vmin.x + (i + 0.5) * (self.vmax.x - self.vmin.x) / self.n
                for i in range(self.n)]

    def enum_centers_y(self):
        return [self.vmin.y + (i + 0.5) * (self.vmax.y - self.vmin.y) / self.n
                for i in range(self.n)]

    def enum_centers_z(self):
        return [self.vmin.z + (i + 0.5) * (self.vmax.z - self.vmin.z) / self.n
                for i in range(self.n)]



tree = OcTree(Vec3(-5.0, -5.0, -5.0), Vec3(5.0, 5.0, 5.0), 64)

#for z in tree.enum_centers_z():
#    for y in tree.enum_centers_y():
#        for x in tree.enum_centers_x():
#            tree.get_leaf(Vec3(x, y, z))

for tri in tris:
    for pt in tri.enum_points(300):
        leaf = tree.get_leaf(pt)
        if leaf is not None:
            leaf.blocked = True


def random_point_sphere():
    while True:
        x = random() - 0.5
        y = random() - 0.5
        z = random() - 0.5
        dist = math.sqrt(x * x + y * y + z * z)
        if dist > 0.5 or dist < 0.001:
            continue
        return Vec3(x, y, z) / dist

def random_point_2d():
    while True:
        x = random() * 2. - 1.
        y = random() * 2. - 1.
        if x * x + y * y < 1.:
            return (x, y)

def ortho_vec(N):
    if abs(N.x) > 0.5:
        v = Vec3(N.y, -N.x, 0.0)
    else:
        v = Vec3(0.0, N.z, -N.y)
    v = v.normalize()
    return v, v.cross(N)

def color(r):
    closest_t = 1e300
    for tri in tris:
        t = tri.hit(r, 0.0001, 1000)
        if 0 < t < closest_t:
            closest_tri = tri
            closest_t = t
    if closest_t < 1e300:
        pt = r.point_at_parameter(closest_t)
        #leaf = tree.get_leaf(pt)
        #if leaf is not None and leaf.blocked:
        #    return Vec3(0, 0, 0)
        N = closest_tri.normal(pt)
        #c = Vec3(abs(N.x), abs(N.y), abs(N.z))
        c = closest_tri.material.diffuse_color

        ray = Ray(pt, SUN_DIRECTION)
        in_sun = ray.B.normalize().dot(N)
        if in_sun > 0.0:
            for tri in tris:
                t = tri.hit(ray, 0.0001, 1000)
                if t > 0:
                    in_sun = 0.0
                    break
            else:
                c += Vec3(0.3, 0.3, 0.3) * in_sun

        if in_sun <= 0.0:
            leaf = tree.get_leaf(pt)
            for i in range(RAYS):
                #direction = random_point_sphere()
                #if direction.dot(N) < 0.0:
                #    direction = -direction

                n1, n2 = ortho_vec(N)
                rx, ry = random_point_2d()
                rz = math.sqrt(1.0 - rx*rx - ry*ry)
                direction = N * rz + n1 * rx + n2 * ry

                k = tree.unit
                while True:
                    leaf1 = tree.get_leaf(pt + direction * k)
                    if leaf1 is None:
                        break
                    if leaf1 is not leaf and leaf1.blocked:
                        c *= 0.8
                        break
                    k += tree.unit

        return c

    unit_direction = r.B.normalize()
    #t = 0.5 * (unit_direction.y + 1.0)
    #return (1.0 - t) * Vec3(1., 1., 1.) + t * Vec3(0.5, 0.7, 1.0)
    k = max(0.0, unit_direction.y)
    v = (1.0 - k) * Vec3(0.64, 0.81, 1.0) + k * Vec3(0.25, 0.49, 1.0)
    return v * 0.8


def main(color=color):
    surf = pygame.surface.Surface((X, Y))
    s = ScreenWrapper(surf)
    #s_surface = ffi.new("float[]", 3 * X * Y)
    #iteration_num = 0

    while True:
        t0 = time.time()
        #frac = 1.0 / float(iteration_num + 1)
        for x in range(X):
            sys.stderr.write(str(x) + '.')
            for y in range(Y):
                #u = float(x + random()) / X
                #v = float(y + random()) / Y
                u = (x + 0.5) / X
                v = (y + 0.5) / Y
                target = lower_left_corner + v * vertical + u * horizontal
                r = Ray(origin, target)
                res = color(r)
                position_key = (x, Y - 1 - y)
                pos_index = 3 * (position_key[1] * X + position_key[0])
                #res += Vec3(s_surface[pos_index],
                #            s_surface[pos_index + 1],
                #            s_surface[pos_index + 2])
                #s_surface[pos_index] = res.x
                #s_surface[pos_index + 1] = res.y
                #s_surface[pos_index + 2] = res.z
                # note: we don't read back s[position_key], because
                # we loose precision by doing so and the effect is
                # quite noticeable after several dozen iterations
                #res *= frac
                if res.x > 1.0: res.x = 1.0
                if res.y > 1.0: res.y = 1.0
                if res.z > 1.0: res.z = 1.0
                s[position_key] = res

        t1 = time.time()
        dt = t1 - t0
        textsurface = myfont.render("iteration %d (%s ms)" % (
            1, #iteration_num + 1,
            int(dt * 1000)), False, (255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        screen.blit(surf, (0, 0))
        screen.blit(textsurface, (10, 10))
        pygame.display.flip()

        raw_input()
        break

        iteration_num += 1

if __name__ == '__main__':
    main()
