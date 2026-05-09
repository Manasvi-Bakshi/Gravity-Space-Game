import pygame
from pygame.math import Vector2
import math

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Additive blending surface for glow effects
        self.glow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
    def _transform(self, camera, pos):
        """Converts a world position to screen coordinates based on camera offset and zoom."""
        x = (pos[0] - camera.pos.x) * camera.zoom + self.width / 2
        y = (pos[1] - camera.pos.y) * camera.zoom + self.height / 2
        return (int(x), int(y))
        
    def _scale(self, camera, size):
        """Scales a size or radius based on camera zoom."""
        return max(1, int(size * camera.zoom))

    def draw_background(self, screen, camera, stars):
        # Deep space dark blue
        screen.fill((8, 8, 16)) 
        for star in stars:
            # Simple infinite parallax starfield
            # Depth based on size (smaller = further = slower movement)
            depth = 4.0 / star["size"] 
            
            # Wrap coordinates around screen dimensions to create infinite space illusion
            x = (star["pos"][0] - (camera.pos.x / depth)) % self.width
            y = (star["pos"][1] - (camera.pos.y / depth)) % self.height
            
            pygame.draw.circle(screen, star["color"], (int(x), int(y)), star["size"])

    def draw_phenomena(self, screen, camera, debris, dust_currents):
        # 1. Ambient Debris (Parallax Depth)
        for p in debris.particles:
            # Slower movement relative to camera based on depth
            x = (p["pos"].x - (camera.pos.x / p["depth"])) % self.width
            y = (p["pos"].y - (camera.pos.y / p["depth"])) % self.height
            
            # Very faint color
            color = (150, 200, 255, p["alpha"])
            size = self._scale(camera, p["size"])
            # Draw directly to glow surface for soft blending
            pygame.draw.circle(self.glow_surface, color, (int(x), int(y)), size)
            
        # 2. Gravitational Dust Currents
        for p in dust_currents.particles:
            pos = self._transform(camera, p["pos"])
            
            # Fade in and out based on lifetime
            ratio = p["lifetime"] / p["max_lifetime"]
            # Parabola for smooth fade in/out: 4 * x * (1 - x)
            fade = 4.0 * ratio * (1.0 - ratio)
            alpha = int(40 * fade) # Extremely faint, max 40/255
            
            color = (100, 150, 255, alpha)
            size = self._scale(camera, 2.0)
            
            # Render to glow surface for soft additive blending
            pygame.draw.circle(self.glow_surface, color, pos, size)

    def draw_collectibles(self, screen, camera, collectibles, particles):
        # 1. Draw collectibles and their short trails
        for c in collectibles:
            # Short orbit trail arc
            if len(c.trail) >= 2:
                points = [self._transform(camera, p) for p in c.trail]
                pygame.draw.lines(self.glow_surface, (0, 150, 200, 80), False, points, self._scale(camera, 2))
                
            # Collectible Shard (Alien/Ancient energy shape)
            pulse = (math.sin(c.time_alive * 3.0) + 1.0) / 2.0 # 0.0 to 1.0
            size = self._scale(camera, 6 + pulse * 2)
            alpha = int(180 + pulse * 75)
            
            c_pos = self._transform(camera, c.pos)
            
            # Diamond shape for ancient/alien feel
            top = (c_pos[0], c_pos[1] - size * 1.5)
            bottom = (c_pos[0], c_pos[1] + size * 1.5)
            left = (c_pos[0] - size, c_pos[1])
            right = (c_pos[0] + size, c_pos[1])
            
            # Rotate points slightly for an organic floating feel
            rot_angle = c.time_alive * 50.0
            def rotate_pt(pt, center, angle):
                s = math.sin(math.radians(angle))
                c_a = math.cos(math.radians(angle))
                pt = (pt[0] - center[0], pt[1] - center[1])
                new_x = pt[0] * c_a - pt[1] * s
                new_y = pt[0] * s + pt[1] * c_a
                return (new_x + center[0], new_y + center[1])
                
            points = [rotate_pt(pt, c_pos, rot_angle) for pt in [top, right, bottom, left]]
            
            # Restrained glow
            pygame.draw.polygon(self.glow_surface, (50, 200, 255, int(alpha * 0.4)), points)
            pygame.draw.polygon(self.glow_surface, (150, 240, 255, alpha), points, width=self._scale(camera, 1))

        # 2. Draw soft collection particle bursts
        for p in particles:
            ratio = p.lifetime / p.max_lifetime
            size = self._scale(camera, max(1, 4 * ratio))
            alpha = int(255 * ratio)
            pos = self._transform(camera, p.pos)
            
            color = (150, 240, 255, alpha)
            glow = (0, 150, 255, int(alpha * 0.5))
            
            pygame.draw.circle(self.glow_surface, glow, pos, size * 2)
            pygame.draw.circle(self.glow_surface, color, pos, size)

    def draw_screen_pulse(self, screen, camera):
        if camera.pulse_intensity > 0:
            alpha = int(camera.pulse_intensity * 255)
            # Very faint teal screen pulse
            pulse_surface = pygame.Surface((self.width, self.height))
            pulse_surface.fill((0, 40, 60))
            pulse_surface.set_alpha(alpha)
            screen.blit(pulse_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def draw_planets(self, screen, camera, planets):
        for planet in planets:
            pos = self._transform(camera, planet.pos)
            base_radius = self._scale(camera, planet.radius)
            
            # 1. Atmospheric Glow (Additive Blending)
            glow_radius = self._scale(camera, planet.radius * 2.5)
            for i in range(5, 0, -1):
                r = int(base_radius + (glow_radius - base_radius) * (i / 5.0))
                alpha = int(40 * (1 - (i / 5.0)))
                color = (50, 100, 200, alpha)
                pygame.draw.circle(self.glow_surface, color, pos, r)
                
            # 2. Planet Core (Solid)
            pygame.draw.circle(screen, (20, 30, 40), pos, base_radius)
            pygame.draw.circle(screen, (60, 120, 180), pos, base_radius, width=self._scale(camera, 3))
            
            # 3. Subtle Debug Orbit ring (for visualizing gravity field scale)
            orbit_radius = self._scale(camera, planet.radius * 4)
            orbit_color = (40, 80, 100)
            pygame.draw.circle(screen, orbit_color, pos, orbit_radius, width=self._scale(camera, 1))

    def draw_snake(self, screen, camera, snake):
        self.glow_surface.fill((0, 0, 0, 0)) 
        
        # 1. Draw velocity trail
        if len(snake.trail) >= 2:
            points = [self._transform(camera, p) for p in snake.trail]
            for i in range(len(points) - 1):
                progress = i / len(points)
                thickness = self._scale(camera, max(1, 4 * progress))
                
                color_val = int(255 * progress)
                trail_color = (0, int(color_val * 0.8), color_val)
                pygame.draw.line(screen, trail_color, points[i], points[i+1], thickness)
                
                glow_color = (0, int(color_val * 0.3), int(color_val * 0.5), 255)
                pygame.draw.line(self.glow_surface, glow_color, points[i], points[i+1], thickness + self._scale(camera, 4))

        # 2. Draw Snake Body (Plasma Ribbon)
        for i in range(1, snake.body_length):
            b_pos = snake.body_positions[i]
            progress = i / snake.body_length 
            inv_progress = 1.0 - progress    
            
            size = self._scale(camera, max(1.0, 11.0 * inv_progress))
            alpha = int(255 * (inv_progress ** 1.5))
            
            core_color = (150, 220, 255, alpha)
            glow_color = (0, 80, 255, int(alpha * 0.5))
            
            pos = self._transform(camera, b_pos)
            
            pygame.draw.circle(self.glow_surface, glow_color, pos, size * 2.5)
            pygame.draw.circle(self.glow_surface, core_color, pos, size)

        # 3. Draw thrust particles
        for p in snake.particles:
            ratio = p.lifetime / p.max_lifetime
            
            if snake.is_boosting:
                color = (int(100 * ratio), int(200 * ratio), 255)
                glow = (0, 50, int(150 * ratio), 255)
            else:
                color = (255, int(150 * ratio), 0)
                glow = (int(150 * ratio), 50, 0, 255)
            
            pos = self._transform(camera, p.pos)
            size = self._scale(camera, 3 * ratio + 1)
            
            pygame.draw.circle(screen, color, pos, size)
            pygame.draw.circle(self.glow_surface, glow, pos, size * 3)

        # 4. Draw Snake Head (Glowing Triangle)
        direction = Vector2(1, 0).rotate(snake.angle)
        right = Vector2(1, 0).rotate(snake.angle + 90)
        
        length = 24
        width = 14
        
        nose = snake.pos + direction * length
        left_wing = snake.pos - direction * (length * 0.4) - right * width
        right_wing = snake.pos - direction * (length * 0.4) + right * width
        
        points = [self._transform(camera, pt) for pt in [nose, left_wing, right_wing]]
        
        pygame.draw.polygon(self.glow_surface, (0, 100, 200, 255), points)
        pygame.draw.polygon(self.glow_surface, (0, 50, 150, 255), points, width=self._scale(camera, 8)) 
        
        pygame.draw.polygon(screen, (200, 240, 255), points)
        pygame.draw.polygon(screen, (255, 255, 255), points, width=self._scale(camera, 2))
        
        # 5. Composite additive glow layer
        screen.blit(self.glow_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
