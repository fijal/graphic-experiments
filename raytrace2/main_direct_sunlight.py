from main import *


SUN_DIRECTION = Vec3(-0.2, 1, 0.1).normalize()
SKY_COLOR = Vec3(0.8, 0.9, 1.0)


def color(r):
    closest_t = 1e300
    for tri in tris:
        t = tri.hit(r, 0.0001, 1000)
        if 0 < t < closest_t:
            closest_tri = tri
            closest_t = t
    if closest_t < 1e300:
        pt = r.point_at_parameter(closest_t)
        r = Ray(pt, SUN_DIRECTION)
        for tri in tris:
            t = tri.hit(r, 0.0001, 1000)
            if t > 0:
                return closest_tri.material.diffuse_color * 0.5
        return closest_tri.material.diffuse_color
    else:
        return SKY_COLOR


if __name__ == '__main__':
    main(color)
