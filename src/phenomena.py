import pygame
from pygame.math import Vector2
import random

class AmbientDebris:
    """
    Tiny, sparse drifting debris to create parallax depth.
    Provides subconscious depth perception without drawing attention.
    """
    def __init__(self, count, width, height):
        self.particles = []
        self.width = width
        self.height = height
        
        for _ in range(count):
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            
            # Very subtle drift
            velocity = Vector2(random.uniform(-5, 5), random.uniform(-5, 5))
            
            # Z-depth for parallax. Higher Z = further away = slower movement relative to camera
            # Depth from 1.5 to 5.0 creates a vast space
            depth = random.uniform(1.5, 5.0) 
            
            self.particles.append({
                "pos": Vector2(x, y),
                "vel": velocity,
                "depth": depth,
                "size": random.uniform(0.5, 1.2),
                # Extremely faint base alpha (5 to 20 out of 255)
                "alpha": random.randint(5, 20) 
            })

    def update(self, dt):
        # Particles drift on their own, independent of camera
        for p in self.particles:
            p["pos"] += p["vel"] * dt


class DustCurrent:
    """
    Extremely faint ribbons that weakly respond to gravity.
    They visualize the "valley" between planets subconsciously.
    """
    def __init__(self, max_particles=40):
        self.particles = []
        self.max_particles = max_particles
        self.spawn_timer = 0.0
        
    def update(self, dt, planets):
        self.spawn_timer += dt
        
        # Slow, sparse spawning
        if self.spawn_timer > 0.8 and len(self.particles) < self.max_particles:
            self.spawn_timer = 0.0
            
            if len(planets) >= 2:
                # Spawn in the general vicinity of the Lagrange point / middle valley
                p1, p2 = planets[0], planets[1]
                midpoint = p1.pos.lerp(p2.pos, random.uniform(0.3, 0.7))
                
                # Add wide scatter so it's a "region" not a point
                spawn_pos = midpoint + Vector2(random.uniform(-500, 500), random.uniform(-500, 500))
                
                self.particles.append({
                    "pos": spawn_pos,
                    "vel": Vector2(random.uniform(-10, 10), random.uniform(-10, 10)),
                    "lifetime": random.uniform(15.0, 30.0), # Very slow fade out
                    "max_lifetime": 30.0
                })
                
        # Update physics
        for p in self.particles:
            p["lifetime"] -= dt
            
            # Apply very weak gravity (e.g. 2% of actual gravity)
            # This makes them drift gently toward planets without accelerating wildly
            total_acc = Vector2(0, 0)
            for planet in planets:
                dir_vec = planet.pos - p["pos"]
                dist = dir_vec.length()
                clamped_dist = max(dist, planet.radius * 2.0) # Larger clamp to avoid slingshotting dust
                
                if clamped_dist > 0:
                    acc = planet.gravity_strength / (clamped_dist ** 2)
                    total_acc += dir_vec.normalize() * acc
                    
            p["vel"] += total_acc * 0.02 * dt
            
            # High atmospheric drag on dust so it flows smoothly and never moves fast
            p["vel"] *= (0.8 ** dt)
            p["pos"] += p["vel"] * dt
            
        self.particles = [p for p in self.particles if p["lifetime"] > 0]
