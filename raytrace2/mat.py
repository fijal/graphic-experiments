
class Material(object):
    def __init__(self, diffuse_color, mirror=0.05, softness=0.03):
        self.diffuse_color = diffuse_color
        self.mirror = mirror
        self.softness = softness
