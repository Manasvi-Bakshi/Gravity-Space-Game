from pygame.math import Vector2

def apply_gravity(planet, entity, dt):
    """
    Applies inverse-square gravity from a planet to an entity.
    entity must have .pos and .velocity Vector2 attributes.
    """
    direction = planet.pos - entity.pos
    distance = direction.length()
    
    # Force clamp: prevent distance from being less than the planet's radius.
    # Without this, gravity explodes toward infinity as distance approaches 0,
    # causing the ship to teleport off-screen at massive speeds if it hits the center.
    clamped_distance = max(distance, planet.radius)
    
    if clamped_distance > 0:
        direction_normalized = direction.normalize()
        
        # Inverse-square formula conceptually: F = G * (m1 * m2) / r^2
        # Since we just want acceleration (a = F / m1), it simplifies to:
        # a = (G * m2) / r^2
        # planet.gravity_strength represents (G * m2).
        acceleration = planet.gravity_strength / (clamped_distance ** 2)
        
        # Gravity directly modifies acceleration, which modifies velocity.
        # This allows momentum to carry the ship into an orbit.
        entity.velocity += direction_normalized * acceleration * dt
