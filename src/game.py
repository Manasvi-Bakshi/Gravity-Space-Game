import pygame
import random
from src.snake import Snake
from src.rendering import Renderer
from src.planet import Planet
from src.physics import apply_gravity
from src.camera import Camera

class Game:
    def __init__(self):
        self.width = 1280
        self.height = 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Gravity Snake")
        
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        self.dt = 0.0
        self.running = True
        
        self.renderer = Renderer(self.width, self.height)
        self.camera = Camera(self.width, self.height)
        
        # Environment
        center_pos = (self.width / 2, self.height / 2)
        self.planet = Planet(center_pos, radius=60, gravity_strength=2500000.0)
        
        # Entities
        start_pos = (self.width / 2 - 300, self.height / 2)
        self.snake = Snake(start_pos)
        self.snake.velocity = pygame.math.Vector2(0, 300)
        
        # Snap camera to snake initially so it doesn't pan wildly at startup
        self.camera.pos = pygame.math.Vector2(start_pos)
        
        self.stars = []
        self._init_stars()

    def _init_stars(self):
        """Generates a static starfield for the background."""
        for _ in range(150):
            # We spawn stars randomly in the screen area. 
            # The renderer will wrap them infinitely as the camera moves.
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.choice([1, 1, 2])
            color_val = random.randint(100, 255)
            color = (color_val, color_val, color_val)
            self.stars.append({"pos": (x, y), "size": size, "color": color})

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
            self.dt = self.clock.tick(self.target_fps) / 1000.0
            
            current_fps = self.clock.get_fps()
            pygame.display.set_caption(f"Gravity Snake - FPS: {current_fps:.1f}")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        keys = pygame.key.get_pressed()
        
        # Physics and Entities
        self.snake.update(self.dt, keys)
        apply_gravity(self.planet, self.snake, self.dt)
        
        # Camera smoothing
        self.camera.update(self.snake, self.dt)

    def draw(self):
        self.renderer.draw_background(self.screen, self.camera, self.stars)
        self.renderer.draw_planet(self.screen, self.camera, self.planet)
        self.renderer.draw_snake(self.screen, self.camera, self.snake)
        pygame.display.flip()
