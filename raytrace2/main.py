
from __future__ import division

import pygame, time, math
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
        self._buf = ffi.cast("char*", screen._pixels_address)

    def fill(self):
        self._screen.fill(0)

    def __setitem__(self, (x, y), c):
        target = (y * X + x) * 4
        self._buf[target + 2] = chr(int((c.x) * 255.99))
        self._buf[target + 1] = chr(int((c.y) * 255.99))
        self._buf[target    ] = chr(int((c.z) * 255.99))

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

mat = Material(Vec3(0.95, 0.2, 0.2))

for i in range(len(tris)):
    a, b, c = tris[i]
    tris[i] = Triangle(Vec3(*a), Vec3(*b), Vec3(*c), mat)
    tris.append(Triangle(Vec3(*a), Vec3(*c), Vec3(*b), mat))  # reversed

mat = Material(Vec3(0.75, 0.75, 0.75))
tris.append(Sphere(Vec3(0, 0, -1), 0.5, mat))

# rounded "floor"
mat = Material(Vec3(0.95, 0.95, 0.0))
tris.append(Sphere(Vec3(0, -100.5, -1), 100, mat))

MAX_BOUNCES = 12
SUN_DIRECTION = Vec3(-0.2, 1, 0.1).normalize()



def random_point():
    while True:
        x = random() * 2. - 1.
        y = random() * 2. - 1.
        z = random() * 2. - 1.
        if x * x + y * y + z * z < 1: # and z * z > (x * x + y * y) * 40:
            return Vec3(x, y, z)

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

def color(r, max_bounces=MAX_BOUNCES):
    if max_bounces == 0:
        return Vec3(0., 0., 0.)
    closest_t = 1e300
    for tri in tris:
        t = tri.hit(r, 0.0001, 1000)
        if 0 < t < closest_t:
            closest_tri = tri
            closest_t = t
    if closest_t < 1e300:
        pt = r.point_at_parameter(closest_t)
        N = closest_tri.normal(pt)
        if random() < closest_tri.material.mirror:
            sr = r.B - 2 * N * N.dot(r.B)
            ray = Ray(pt, sr)
            return color(ray, max_bounces-1)
        else:
            # this should follow the Lambertian model of diffuse surfaces
            # by computing a source direction 'sr' that doesn't depend on
            # the output direction 'r', and with more probability to be
            # near the normal N than near the plane orthogonal to N
            rx, ry = random_point_2d()
            rz = math.sqrt(1.0 - rx*rx - ry*ry)
            n1, n2 = ortho_vec(N)
            sr = N * rz + n1 * rx + n2 * ry
            ray = Ray(pt, sr)
            c1 = color(ray, max_bounces-1)
            c2 = closest_tri.material.diffuse_color
            #
            ray = Ray(pt, SUN_DIRECTION + random_point() * 0.1)
            in_sun = ray.B.normalize().dot(N)
            if in_sun > 0.0:
                for tri in tris:
                    t = tri.hit(ray, 0.0001, 1000)
                    if t > 0:
                        in_sun = 0.0
                        break
            if in_sun > 0.0:
                c1 += Vec3(0.2, 0.2, 0.2) * in_sun
            return Vec3(c1.x * c2.x, c1.y * c2.y, c1.z * c2.z)
    unit_direction = r.B.normalize()
    #t = 0.5 * (unit_direction.y + 1.0)
    #return (1.0 - t) * Vec3(1., 1., 1.) + t * Vec3(0.5, 0.7, 1.0)
    k = max(0.0, unit_direction.y)
    v = (1.0 - k) * Vec3(0.8, 0.9, 1.0) + k * Vec3(0.5, 0.7, 1.0)
    return v

def main(color=color):
    surf = pygame.surface.Surface((X, Y))
    s = ScreenWrapper(surf)
    s_surface = ffi.new("float[]", 3 * X * Y)
    iteration_num = 0

    while True:
        t0 = time.time()
        old_frac = iteration_num / float(iteration_num + 1)
        new_frac = 1.0 / float(iteration_num + 1)
        for x in range(X):
            for y in range(Y):
                u = float(x + random()) / X
                v = float(y + random()) / Y
                target = lower_left_corner + v * vertical + u * horizontal
                r = Ray(origin, target)
                res = color(r)
                position_key = (x, Y - 1 - y)
                pos_index = 3 * (position_key[1] * X + position_key[0])
                old_res = Vec3(s_surface[pos_index],
                               s_surface[pos_index + 1],
                               s_surface[pos_index + 2])
                res = old_res * old_frac + res * new_frac
                s_surface[pos_index] = res.x
                s_surface[pos_index + 1] = res.y
                s_surface[pos_index + 2] = res.z
                # note: we don't read back s[position_key], because
                # we loose precision by doing so and the effect is
                # quite noticeable after several dozen iterations
                if res.x > 1.0: res.x = 1.0
                if res.y > 1.0: res.y = 1.0
                if res.z > 1.0: res.z = 1.0
                s[position_key] = res

        t1 = time.time()
        dt = t1 - t0
        textsurface = myfont.render("iteration %d (%s ms)" % (
            iteration_num + 1,
            int(dt * 1000)), False, (255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        screen.blit(surf, (0, 0))
        screen.blit(textsurface, (10, 10))
        pygame.display.flip()
        iteration_num += 1

if __name__ == '__main__':
    main()
