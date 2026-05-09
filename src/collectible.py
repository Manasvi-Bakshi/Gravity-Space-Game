import pygame
from pygame.math import Vector2
import random
import math

class CollectibleParticle:
    def __init__(self, pos, velocity, lifetime):
        self.pos = Vector2(pos)
        self.velocity = Vector2(velocity)
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self, dt):
        self.pos += self.velocity * dt
        self.lifetime -= dt

class Collectible:
    def __init__(self, planet):
        self.planet = planet

        # Trail state
        self.trail = []
        self.trail_timer = 0.0

        # Initialize BEFORE respawn()
        # because _calculate_pos() depends on it
        self.time_alive = random.uniform(0, 100)

        self.respawn()

    def respawn(self):
        # Layered orbits
        min_radius = self.planet.radius * 2.5
        max_radius = self.planet.radius * 7.0

        self.base_orbit_radius = random.uniform(min_radius, max_radius)
        self.orbit_radius = self.base_orbit_radius

        self.angle = random.uniform(0, 360)

        # Kepler-inspired orbit scaling
        # Further objects orbit slower
        base_speed = 8000.0
        self.angular_velocity = base_speed / (self.orbit_radius ** 1.5)

        # Random orbit direction
        if random.choice([True, False]):
            self.angular_velocity *= -1

        self.pos = self._calculate_pos()

        self.trail.clear()
        self.trail_timer = 0.0

    def _calculate_pos(self):
        # Slight organic wobble
        wobble = math.sin(self.time_alive * 2.0) * (
            self.base_orbit_radius * 0.03
        )

        self.orbit_radius = self.base_orbit_radius + wobble

        offset = Vector2(self.orbit_radius, 0).rotate(self.angle)

        return self.planet.pos + offset

    def update(self, dt):
        self.time_alive += dt

        self.angle = (
            self.angle + self.angular_velocity * dt
        ) % 360.0

        self.pos = self._calculate_pos()

        # Short trailing arc
        self.trail_timer += dt

        if self.trail_timer >= 0.05:
            self.trail_timer = 0.0

            self.trail.append(Vector2(self.pos))

            if len(self.trail) > 12:
                self.trail.pop(0)