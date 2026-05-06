from pygame.math import Vector2

class Planet:
    def __init__(self, pos, radius, gravity_strength=2000000.0):
        self.pos = Vector2(pos)
        self.radius = radius
        # gravity_strength acts as (G * M) in the gravity equation.
        # It's a high number because inverse-square falls off very quickly.
        self.gravity_strength = gravity_strength
