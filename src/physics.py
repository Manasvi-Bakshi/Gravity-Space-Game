from pygame.math import Vector2

def apply_gravity(planets, entity, dt):
    """
    Applies inverse-square gravity from multiple planets to an entity.
    entity must have .pos and .velocity Vector2 attributes.
    """
    total_acceleration_vector = Vector2(0, 0)
    
    for planet in planets:
        direction = planet.pos - entity.pos
        distance = direction.length()
        
        # Force clamp: prevent distance from being less than the planet's radius.
        clamped_distance = max(distance, planet.radius)
        
        if clamped_distance > 0:
            direction_normalized = direction.normalize()
            
            # Inverse-square formula conceptually: a = (G * m2) / r^2
            acceleration = planet.gravity_strength / (clamped_distance ** 2)
            
            total_acceleration_vector += direction_normalized * acceleration
            
    # Gravity directly modifies acceleration, which modifies velocity.
    entity.velocity += total_acceleration_vector * dt
