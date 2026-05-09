import pygame
from pygame.math import Vector2
import random

class Particle:
    def __init__(self, pos, velocity, lifetime):
        self.pos = Vector2(pos)
        self.velocity = Vector2(velocity)
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self, dt):
        self.pos += self.velocity * dt
        self.lifetime -= dt

class Snake:
    # Configurable Physics Constants
    THRUST_POWER = 500.0
    BOOST_POWER = 1200.0
    TURN_SPEED = 250.0  # degrees per second
    MAX_SPEED = 800.0
    # DAMPING acts as space friction. 0.98 means 98% of velocity remains after 1 second.
    # We lowered friction significantly so the ship can actually maintain an orbit.
    DAMPING = 0.98 
    
    def __init__(self, start_pos):
        self.pos = Vector2(start_pos)
        self.velocity = Vector2(0, 0)
        # 0 degrees in Pygame math usually points right (1, 0). 
        # -90 degrees points up.
        self.angle = -90.0 
        
        # Visual state properties
        self.is_thrusting = False
        self.is_boosting = False
        
        # Trail and Particles state
        self.trail = []
        self.trail_timer = 0.0
        self.trail_interval = 0.03
        self.max_trail_length = 25
        
        self.particles = []
        
        # Plasma Ribbon
        self.body_length = 35
        self.segment_spacing = 3.0
        self.path_history = [Vector2(start_pos)]
        self.body_positions = [Vector2(start_pos) for _ in range(self.body_length)]
        
        # Finalization state
        self.is_dead = False
        self.disintegration_timer = 0.0
        self.spawn_timer = 0.0

    def update(self, dt, keys):
        if dt <= 0:
            return
            
        if self.is_dead:
            self.disintegration_timer += dt
            self.velocity *= (0.96 ** dt)
            self.pos += self.velocity * dt
            self._update_particles(dt)
            self._update_body(dt)
            return

        self.spawn_timer += dt

        self.is_thrusting = False
        self.is_boosting = False
        
        # 1. Difficulty Scaling (Inertia and Rotation)
        # Higher length increases mass, making the snake feel 'heavier'
        length_offset = max(0, self.body_length - 35)
        mass_factor = 1.0 + (length_offset * 0.005) # Very subtle inertia scaling
        rotational_dampening = 1.0 + (length_offset * 0.002)
        
        current_turn_speed = self.TURN_SPEED / rotational_dampening
        
        # 2. Handle Smooth Rotation
        if keys[pygame.K_a]:
            self.angle -= current_turn_speed * dt
        if keys[pygame.K_d]:
            self.angle += current_turn_speed * dt
            
        self.angle %= 360.0
        
        # Forward direction vector
        direction = Vector2(1, 0).rotate(self.angle)
        lateral_dir = direction.rotate(90)
        
        # 3. Handle Multi-Directional Thrust
        acceleration = Vector2(0, 0)
        
        # Main Forward Thrust
        if keys[pygame.K_w]:
            self.is_thrusting = True
            if keys[pygame.K_SPACE]:
                self.is_boosting = True
                power = self.BOOST_POWER
            else:
                power = self.THRUST_POWER
            acceleration += direction * power
            self._spawn_particles(direction, dt)
            
        # Reverse / Stabilization Thrust (S)
        if keys[pygame.K_s]:
            acceleration -= direction * (self.THRUST_POWER * 0.5)
            
        # Lateral Correction Thrusters (Q / E)
        lateral_power = self.THRUST_POWER * 0.4
        if keys[pygame.K_q]:
            acceleration -= lateral_dir * lateral_power
        if keys[pygame.K_e]:
            acceleration += lateral_dir * lateral_power
            
        # Apply Mass to acceleration (Heavier snake = slower acceleration)
        acceleration /= mass_factor
            
        # 4. Physics Integration
        self.velocity += acceleration * dt
        self.velocity *= (self.DAMPING ** dt)
        
        if self.velocity.length() > self.MAX_SPEED:
            self.velocity.scale_to_length(self.MAX_SPEED)
            
        self.pos += self.velocity * dt
        
        # 5. Self-Collision Detection
        if self.check_self_collision():
            self.is_dead = True
        
        # 6. Update Visual Effects
        self._update_trail(dt)
        self._update_particles(dt)
        self._update_body(dt)

    def check_self_collision(self):
        # 1. Grace Period: No collision for first few seconds of life
        if self.spawn_timer < 3.0:
            return False
            
        # 2. Minimum Length: Only collide once we have grown significantly
        # (Start length is 35, so we need to collect at least 5-10 fragments)
        if self.body_length < 45:
            return False
            
        # 3. Skip 'Neck' segments: Ignore segments closest to the head
        # We skip more segments as we grow to ensure the 'loop' is large enough to be fair
        safe_segments = 25 
        
        # Head collision radius
        head_radius = 12.0
        
        for i in range(safe_segments, min(self.body_length, len(self.body_positions))):
            dist = self.pos.distance_to(self.body_positions[i])
            if dist < head_radius:
                # DEBUG PRINT for investigation
                print(f"Collision! Seg:{i} Dist:{dist:.2f} Len:{self.body_length}")
                return True
        return False

    def _update_body(self, dt):
        # 0. Defensive growth: Ensure body_positions matches body_length
        while len(self.body_positions) < self.body_length:
            self.body_positions.append(Vector2(self.pos))
            
        # Record path if moved enough to avoid redundant dense points
        if self.path_history[-1].distance_to(self.pos) > 1.0:
            self.path_history.append(Vector2(self.pos))
            
        self.body_positions[0] = Vector2(self.pos)
        
        current_dist = 0.0
        hist_idx = len(self.path_history) - 1
        
        # Walk backward along path history to place each segment exactly 'segment_spacing' apart
        for i in range(1, self.body_length):
            target_dist = i * self.segment_spacing
            
            while hist_idx > 0:
                p1 = self.path_history[hist_idx]
                p2 = self.path_history[hist_idx - 1]
                dist_p1_p2 = p1.distance_to(p2)
                
                if current_dist + dist_p1_p2 >= target_dist:
                    excess = target_dist - current_dist
                    t = excess / dist_p1_p2 if dist_p1_p2 > 0 else 0
                    self.body_positions[i] = p1.lerp(p2, t)
                    break
                else:
                    current_dist += dist_p1_p2
                    hist_idx -= 1
            else:
                self.body_positions[i] = Vector2(self.path_history[0])
                
        # Prune history to prevent memory leaks (keep enough points for full body length)
        # 35 segments * 3 spacing = 105 length. Appending every 1 unit means ~105 points max needed.
        # Expand path history as length grows
        history_limit = int(self.body_length * self.segment_spacing + 50)
        if len(self.path_history) > history_limit:
            self.path_history = self.path_history[-history_limit:]

    def _spawn_particles(self, direction, dt):
        # Spawn particles shooting opposite to movement direction with some spread
        spread_angle = self.angle + 180 + random.uniform(-20, 20)
        part_dir = Vector2(1, 0).rotate(spread_angle)
        
        speed = random.uniform(100, 300)
        if self.is_boosting:
            speed = random.uniform(300, 600)
            
        # Particles inherit a fraction of the ship's current velocity
        part_vel = part_dir * speed + self.velocity * 0.3
        lifetime = random.uniform(0.2, 0.4)
        
        # Spawn at the rear of the ship
        spawn_pos = self.pos - direction * 15
        self.particles.append(Particle(spawn_pos, part_vel, lifetime))

    def _update_particles(self, dt):
        for p in self.particles:
            p.update(dt)
        # Keep only particles that haven't died
        self.particles = [p for p in self.particles if p.lifetime > 0]

    def _update_trail(self, dt):
        # Record position periodically for the velocity trail
        self.trail_timer += dt
        if self.trail_timer >= self.trail_interval:
            self.trail_timer = 0
            # Only record if moving significantly
            if self.velocity.length() > 10:
                self.trail.append(Vector2(self.pos))
                if len(self.trail) > self.max_trail_length:
                    self.trail.pop(0)
            else:
                # Shrink trail gracefully when stopped
                if self.trail:
                    self.trail.pop(0)
