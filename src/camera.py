from pygame.math import Vector2
import math

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # World space position of the camera's center
        self.pos = Vector2(0, 0)
        self.zoom = 1.0
        
        # How fast the camera interpolates towards the target (stiffness)
        self.lerp_speed = 4.0 
        
    def update(self, target, dt):
        """Smoothly tracks a target with framerate-independent lerp."""
        if dt <= 0:
            return
            
        # Framerate-independent lerp formulation: t = 1 - e^(-speed * dt)
        t = 1.0 - math.exp(-self.lerp_speed * dt)
        
        # Positional interpolation
        self.pos = self.pos.lerp(target.pos, t)
        
        # Zoom out slightly at high speeds to give a broader view of the environment
        speed = target.velocity.length()
        target_zoom = 1.0 - (min(speed, 1000.0) / 1000.0) * 0.4
        
        # Smoothly interpolate zoom as well, slightly slower than position
        self.zoom += (target_zoom - self.zoom) * (t * 0.5)
