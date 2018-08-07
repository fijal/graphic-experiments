
from __future__ import division

from vec import Vec3, Ray, EPSILON
from hypothesis import given, strategies as s

float_strat = s.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)
vec = s.tuples(float_strat, float_strat, float_strat)

@given(vec, vec)
def test_ops(t1, t2):
    x1, y1, z1 = t1
    x2, y2, z2 = t2
    assert Vec3(x1, y1, z1) + Vec3(x2, y2, z2) == Vec3(x1 + x2, y1 + y2, z1 + z2)
    assert Vec3(x1, y1, z1) - Vec3(x2, y2, z2) == Vec3(x1 - x2, y1 - y2, z1 - z2)

@given(vec, float_strat)
def test_mul_int(v, t):
    v = Vec3(*v)
    assert t * v == v * t
    assert t * v == Vec3(t * v.x, t * v.y, t * v.z)
    if t != 0:
        assert v / t == Vec3(v.x / t, v.y / t, v.z / t)

@given(vec)
def test_normalize(v):
    v = Vec3(*v)
    if v.length() > 1e-20:
        assert abs(v.normalize().length() - 1.0) < 1e-10
        r = Ray(Vec3(0, 0, 0), v.normalize())
        assert (r.point_at_parameter(v.length()) - v).length() < EPSILON
