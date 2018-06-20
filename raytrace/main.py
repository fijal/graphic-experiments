
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
        self._buf[y * X * 4 + x * 4 + 1] = chr(int(math.sqrt(c.x) * 255.99))
        self._buf[y * X * 4 + x * 4 + 2] = chr(int(math.sqrt(c.y) * 255.99))
        self._buf[y * X * 4 + x * 4 + 3] = chr(int(math.sqrt(c.z) * 255.99))

origin = Vec3(0., 0., 0.)
vertical = Vec3(0.0, 2.0, 0.0)
horizontal = Vec3(4.0, 0.0, 0.0)
lower_left_corner = Vec3(-2.0, -1.0, -1.0)

tris = [
    [(0, 0.8, -1), (-0.8, 0, -1), (0, 0, -0.4)]
#    [(0, 0, -1), (1, 0, -2), (0, 1, -2)],
#    [(0, 0, -1), (0, 1, -2), (-1, 0, -2)],
#    [(0, 0, -1), (-1, 0, -2), (0, -1, -2)],
    ]

mat = Material()

for i in range(len(tris)):
    a, b, c = tris[i]
    tris[i] = Triangle(Vec3(*a), Vec3(*b), Vec3(*c), mat)

tris.append(Sphere(Vec3(0, 0, -1), 0.5, mat))
tris.append(Sphere(Vec3(0, -100.5, -1), 100, mat))

def random_point():
    while True:
        x = random() * 2. - 1.
        y = random() * 2. - 1.
        z = random() * 2. - 1.
        if x * x + y * y + z * z < 1 and z * z > (x * x + y * y) * 40:
            return Vec3(x, y, z)

def min_index(l):
    index = -1
    value = 1000000000
    for i in range(len(l)):
        if value > l[i][0]:
            value = l[i][0]
            index = i
    return index

def color(r, max_bounces=3):
    if max_bounces == 0:
        return Vec3(0., 0., 0.)
    candidates = []
    for tri in tris:
        t = tri.hit(r, 0.001, 1000)
        if t > 0:
            pt = r.point_at_parameter(t)
            candidates.append((t, pt, tri.normal(pt)))
    if candidates:
        min = min_index(candidates)
        N = candidates[min][2]
        pt = candidates[min][1]
        r = Ray(pt, pt + N + random_point())
        return 0.5 * color(r, max_bounces-1)
        return 0.5 * Vec3(N.x + 1, N.y + 1, N.z + 1)
    unit_direction = r.B.normalize()
    t = 0.5 * (unit_direction.y + 1.0)
    return (1.0 - t) * Vec3(1., 1., 1.) + t * Vec3(0.5, 0.7, 1.0)

def main():
    done = False
    t0 = time.time()
    surf = pygame.surface.Surface((X, Y))
    s = ScreenWrapper(surf)

    t0 = time.time()
    for x in range(X):
        for y in range(Y):
            res = Vec3(0, 0, 0)
            for i in range(4):
                u = float(x + random()) / X
                v = float(y + random()) / Y
                target = lower_left_corner + v * vertical + u * horizontal
                r = Ray(origin, target)
                res += color(r)
            s[x, Y - y] = res / 4
    t1 = time.time()
    dt = t1 - t0
    textsurface = myfont.render(str(int(dt * 1000)) + "ms", False, (255, 255, 255))

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_q):
                done = True
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_w):
                origin.z -= 0.1
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_s):
                origin.z += 0.1
        screen.fill(0)
        
        screen.blit(surf, (0, 0))
        screen.blit(textsurface, (10, 10))
        pygame.display.flip()

if __name__ == '__main__':
    main()
