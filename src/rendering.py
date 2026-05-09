import pygame
from pygame.math import Vector2
import math

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Additive blending surface for glow effects
        self.glow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Minimalist HUD fonts
        pygame.font.init()
        self.font = pygame.font.SysFont("Consolas, monaco, monospace", 16)
        self.large_font = pygame.font.SysFont("Consolas, monaco, monospace", 28)
        
    def clear_glow_surface(self):
        """Clears the additive glow layer at the start of each frame."""
        self.glow_surface.fill((0, 0, 0, 0))
        
    def _transform(self, camera, pos):
        """Converts a world position to screen coordinates based on camera offset and zoom."""
        x = (pos[0] - camera.pos.x) * camera.zoom + self.width / 2
        y = (pos[1] - camera.pos.y) * camera.zoom + self.height / 2
        return (int(x), int(y))
        
    def _scale(self, camera, size):
        """Scales a size or radius based on camera zoom."""
        return max(1, int(size * camera.zoom))

    def draw_background(self, screen, camera, stars, resonance=1.0):
        # Deep space dark blue (dimmed by resonance)
        bg_color = (int(8 * resonance), int(8 * resonance), int(16 * resonance))
        screen.fill(bg_color) 
        for star in stars:
            depth = 4.0 / star["size"] 
            x = (star["pos"][0] - (camera.pos.x / depth)) % self.width
            y = (star["pos"][1] - (camera.pos.y / depth)) % self.height
            
            # Dim star color by resonance
            color = tuple(int(c * resonance) for c in star["color"])
            pygame.draw.circle(screen, color, (int(x), int(y)), star["size"])

    def draw_phenomena(self, screen, camera, debris, dust_currents, resonance=1.0):
        # 1. Ambient Debris (Parallax Depth)
        for p in debris.particles:
            x = (p["pos"].x - (camera.pos.x / p["depth"])) % self.width
            y = (p["pos"].y - (camera.pos.y / p["depth"])) % self.height
            
            # Dim alpha by resonance
            alpha = int(p["alpha"] * resonance)
            if alpha <= 0: continue
            
            color = (150, 200, 255, alpha)
            size = self._scale(camera, p["size"])
            pygame.draw.circle(self.glow_surface, color, (int(x), int(y)), size)
            
        # 2. Gravitational Dust Currents
        for p in dust_currents.particles:
            pos = self._transform(camera, p["pos"])
            ratio = p["lifetime"] / p["max_lifetime"]
            fade = 4.0 * ratio * (1.0 - ratio)
            
            # Combined fade and resonance
            alpha = int(40 * fade * resonance) 
            if alpha <= 0: continue
            
            color = (100, 150, 255, alpha)
            size = self._scale(camera, 2.0)
            pygame.draw.circle(self.glow_surface, color, pos, size)

    def draw_collectibles(self, screen, camera, collectibles, particles, resonance=1.0):
        # 1. Draw collectibles and their short trails
        for c in collectibles:
            if len(c.trail) >= 2:
                points = [self._transform(camera, p) for p in c.trail]
                pygame.draw.lines(self.glow_surface, (0, 150, 200, int(80 * resonance)), False, points, self._scale(camera, 2))
                
            pulse = (math.sin(c.time_alive * 3.0) + 1.0) / 2.0
            size = self._scale(camera, 6 + pulse * 2)
            alpha = int((180 + pulse * 75) * resonance)
            if alpha <= 0: continue
            
            c_pos = self._transform(camera, c.pos)
            top = (c_pos[0], c_pos[1] - size * 1.5)
            bottom = (c_pos[0], c_pos[1] + size * 1.5)
            left = (c_pos[0] - size, c_pos[1])
            right = (c_pos[0] + size, c_pos[1])
            
            rot_angle = c.time_alive * 50.0
            def rotate_pt(pt, center, angle):
                s = math.sin(math.radians(angle))
                c_a = math.cos(math.radians(angle))
                pt = (pt[0] - center[0], pt[1] - center[1])
                new_x = pt[0] * c_a - pt[1] * s
                new_y = pt[0] * s + pt[1] * c_a
                return (new_x + center[0], new_y + center[1])
                
            points = [rotate_pt(pt, c_pos, rot_angle) for pt in [top, right, bottom, left]]
            
            pygame.draw.polygon(self.glow_surface, (50, 200, 255, int(alpha * 0.4)), points)
            pygame.draw.polygon(self.glow_surface, (150, 240, 255, alpha), points, width=self._scale(camera, 1))

        # 2. Draw soft collection particle bursts
        for p in particles:
            ratio = p.lifetime / p.max_lifetime
            size = self._scale(camera, max(1, 4 * ratio))
            alpha = int(255 * ratio * resonance)
            if alpha <= 0: continue
            
            pos = self._transform(camera, p.pos)
            color = (150, 240, 255, alpha)
            glow = (0, 150, 255, int(alpha * 0.5))
            pygame.draw.circle(self.glow_surface, glow, pos, size * 2)
            pygame.draw.circle(self.glow_surface, color, pos, size)

    def draw_screen_pulse(self, screen, camera, resonance=1.0):
        if camera.pulse_intensity > 0:
            # FIX: Scale RGB color directly by intensity to avoid BLEND_RGB_ADD ignoring alpha
            # and use resonance to dim the pulse in deep space.
            intensity = camera.pulse_intensity * resonance
            color = (0, int(40 * intensity), int(60 * intensity))
            
            pulse_surface = pygame.Surface((self.width, self.height))
            pulse_surface.fill(color)
            screen.blit(pulse_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def draw_planets(self, screen, camera, planets, resonance=1.0):
        for planet in planets:
            pos = self._transform(camera, planet.pos)
            base_radius = self._scale(camera, planet.radius)
            
            # 1. Atmospheric Glow (Additive Blending)
            glow_radius = self._scale(camera, planet.radius * 2.5)
            for i in range(5, 0, -1):
                r = int(base_radius + (glow_radius - base_radius) * (i / 5.0))
                alpha = int(40 * (1 - (i / 5.0)) * resonance)
                if alpha <= 0: continue
                color = (50, 100, 200, alpha)
                pygame.draw.circle(self.glow_surface, color, pos, r)
                
            # 2. Planet Core (Solid)
            core_color = tuple(int(c * resonance) for c in (20, 30, 40))
            rim_color = tuple(int(c * resonance) for c in (60, 120, 180))
            pygame.draw.circle(screen, core_color, pos, base_radius)
            pygame.draw.circle(screen, rim_color, pos, base_radius, width=self._scale(camera, 3))
            
            # 3. Subtle Debug Orbit ring
            orbit_color = tuple(int(c * resonance) for c in (40, 80, 100))
            pygame.draw.circle(screen, orbit_color, pos, self._scale(camera, planet.radius * 4), width=self._scale(camera, 1))

    def draw_snake(self, screen, camera, snake, resonance=1.0):
        # Disintegration effect multiplier
        death_fade = 1.0
        if snake.is_dead:
            death_fade = max(0.0, 1.0 - (snake.disintegration_timer / 2.5))
        
        # 1. Draw velocity trail
        if len(snake.trail) >= 2:
            points = [self._transform(camera, p) for p in snake.trail]
            for i in range(len(points) - 1):
                progress = i / len(points)
                thickness = self._scale(camera, max(1, 4 * progress))
                
                alpha_mult = progress * resonance * death_fade
                color_val = int(255 * alpha_mult)
                trail_color = (0, int(color_val * 0.8), color_val)
                pygame.draw.line(screen, trail_color, points[i], points[i+1], thickness)
                
                glow_color = (0, int(color_val * 0.3), int(color_val * 0.5), 255)
                pygame.draw.line(self.glow_surface, glow_color, points[i], points[i+1], thickness + self._scale(camera, 4))

        # 2. Draw Snake Body (Plasma Ribbon)
        # DEFENSIVE: Use actual list length to prevent crash during growth/restart
        display_length = min(snake.body_length, len(snake.body_positions))
        for i in range(1, display_length):
            b_pos = snake.body_positions[i]
            progress = i / snake.body_length 
            inv_progress = 1.0 - progress    
            
            # Ribbon destabilizes gradually when dead
            destabilize = 0.0
            if snake.is_dead:
                destabilize = math.sin(snake.disintegration_timer * 10.0 + i) * (snake.disintegration_timer * 5.0)
            
            size = self._scale(camera, max(1.0, 11.0 * inv_progress))
            alpha = int(255 * (inv_progress ** 1.5) * resonance * death_fade)
            if alpha <= 0: continue
            
            core_color = (150, 220, 255, alpha)
            glow_color = (0, 80, 255, int(alpha * 0.5))
            
            pos = self._transform(camera, b_pos)
            pos = (pos[0] + int(destabilize), pos[1] + int(destabilize))
            
            pygame.draw.circle(self.glow_surface, glow_color, pos, size * 2.5)
            pygame.draw.circle(self.glow_surface, core_color, pos, size)

        # 3. Draw thrust particles
        for p in snake.particles:
            ratio = p.lifetime / p.max_lifetime
            alpha = int(255 * ratio * resonance * death_fade)
            if alpha <= 0: continue
            
            pos = self._transform(camera, p.pos)
            size = self._scale(camera, 3 * ratio + 1)
            
            if snake.is_boosting:
                color = (int(100 * ratio), int(200 * ratio), 255)
                glow = (0, 50, int(150 * ratio), alpha)
            else:
                color = (255, int(150 * ratio), 0)
                glow = (int(150 * ratio), 50, 0, alpha)
            
            pygame.draw.circle(screen, color, pos, size)
            pygame.draw.circle(self.glow_surface, glow, pos, size * 3)

        # 4. Draw Snake Head (Glowing Triangle)
        if not snake.is_dead:
            direction = Vector2(1, 0).rotate(snake.angle)
            right = Vector2(1, 0).rotate(snake.angle + 90)
            length = 24
            width = 14
            nose = snake.pos + direction * length
            left_wing = snake.pos - direction * (length * 0.4) - right * width
            right_wing = snake.pos - direction * (length * 0.4) + right * width
            points = [self._transform(camera, pt) for pt in [nose, left_wing, right_wing]]
            
            h_alpha = int(255 * resonance)
            pygame.draw.polygon(self.glow_surface, (0, 100, 200, h_alpha), points)
            pygame.draw.polygon(self.glow_surface, (0, 50, 150, h_alpha), points, width=self._scale(camera, 8)) 
            pygame.draw.polygon(screen, (int(200 * resonance), int(240 * resonance), int(255 * resonance)), points)
            pygame.draw.polygon(screen, (int(255 * resonance), int(255 * resonance), int(255 * resonance)), points, width=self._scale(camera, 2))
        
        # 5. Composite additive glow layer
        screen.blit(self.glow_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def draw_hud(self, screen, snake, resonance, score):
        # Minimalist Monospace HUD
        y_offset = 30
        line_height = 25
        
        # RESONANCE (Subtle bar)
        res_label = self.font.render("RESONANCE", True, (100, 200, 255))
        res_label.set_alpha(int(150 * resonance))
        screen.blit(res_label, (40, y_offset))
        
        bar_width = 100
        pygame.draw.rect(screen, (20, 40, 60), (40, y_offset + 20, bar_width, 4))
        pygame.draw.rect(screen, (100, 220, 255), (40, y_offset + 20, int(bar_width * resonance), 4))
        
        # LENGTH & DEPTH
        len_txt = self.font.render(f"LENGTH {snake.body_length}", True, (200, 240, 255))
        len_txt.set_alpha(int(180 * resonance))
        screen.blit(len_txt, (40, y_offset + 45))
        
        score_txt = self.font.render(f"DEPTH  {score}", True, (200, 240, 255))
        score_txt.set_alpha(int(180 * resonance))
        screen.blit(score_txt, (40, y_offset + 65))
        
        if snake.is_dead:
            # Failure message
            msg = self.large_font.render("RESONANCE COLLAPSED", True, (255, 100, 100))
            restart = self.font.render("PRESS [SPACE] TO RE-ESTABLISH", True, (200, 200, 200))
            
            # Pulsing alpha
            alpha = int(127 + 127 * math.sin(pygame.time.get_ticks() * 0.005))
            msg.set_alpha(alpha)
            restart.set_alpha(alpha)
            
            screen.blit(msg, (self.width // 2 - msg.get_width() // 2, self.height // 2 - 40))
            screen.blit(restart, (self.width // 2 - restart.get_width() // 2, self.height // 2 + 10))
