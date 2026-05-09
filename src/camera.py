from pygame.math import Vector2
import math

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # World space position of the camera's center
        self.base_pos = Vector2(0, 0)
        self.pos = Vector2(0, 0)
        self.zoom = 1.0
        
        # How fast the camera interpolates towards the target (stiffness)
        self.lerp_speed = 4.0 
        
        # Feedback effects
        self.impulse = Vector2(0, 0)
        self.pulse_intensity = 0.0
        
    def update(self, target, dt):
        """Smoothly tracks a target with framerate-independent lerp."""
        if dt <= 0:
            return
            
        # Framerate-independent lerp formulation: t = 1 - e^(-speed * dt)
        t = 1.0 - math.exp(-self.lerp_speed * dt)
        
        # Positional interpolation
        self.base_pos = self.base_pos.lerp(target.pos, t)
        
        # Handle subtle tactile feedback
        self.impulse *= (0.85 ** (dt * 60.0))
        self.pos = self.base_pos + self.impulse
        
        if self.pulse_intensity > 0:
            self.pulse_intensity = max(0.0, self.pulse_intensity - dt * 2.0)
        
        # Zoom out slightly at high speeds to give a broader view of the environment
        speed = target.velocity.length()
        target_zoom = 1.0 - (min(speed, 1000.0) / 1000.0) * 0.4
        
        # Smoothly interpolate zoom as well, slightly slower than position
        self.zoom += (target_zoom - self.zoom) * (t * 0.5)

    def apply_collection_feedback(self, snake_velocity):
        # A gentle nudge in the direction of movement (adds tactile momentum without violent shake)
        if snake_velocity.length() > 0:
            direction = snake_velocity.normalize()
            self.impulse = direction * 10.0
        self.pulse_intensity = 0.15 # Extremely faint additive screen pulse
