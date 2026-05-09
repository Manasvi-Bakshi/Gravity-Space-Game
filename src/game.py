import pygame
import random
from src.snake import Snake
from src.rendering import Renderer
from src.planet import Planet
from src.physics import apply_gravity
from src.camera import Camera
from src.collectible import Collectible, CollectibleParticle
from src.phenomena import AmbientDebris, DustCurrent

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
        # Binary system with generous spacing. Slightly reduced gravity for each.
        self.planets = [
            Planet((self.width / 2 - 450, self.height / 2), radius=50, gravity_strength=1600000.0),
            Planet((self.width / 2 + 450, self.height / 2), radius=60, gravity_strength=1900000.0)
        ]
        
        # Entities
        # Start in the space between the planets
        start_pos = (self.width / 2, self.height / 2 - 250)
        self.snake = Snake(start_pos)
        self.snake.velocity = pygame.math.Vector2(450, 0)
        
        # Distribute collectibles randomly across planets
        self.collectibles = [Collectible(random.choice(self.planets)) for _ in range(20)]
        self.collection_particles = []
        
        # Snap camera to snake initially so it doesn't pan wildly at startup
        self.camera.base_pos = pygame.math.Vector2(start_pos)
        self.camera.pos = pygame.math.Vector2(start_pos)
        
        self.stars = []
        self._init_stars()
        
        # Space Phenomena
        self.ambient_debris = AmbientDebris(100, self.width, self.height)
        self.dust_current = DustCurrent(max_particles=40)

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
        apply_gravity(self.planets, self.snake, self.dt)
        
        for c in self.collectibles:
            c.update(self.dt)
            # Gentle radius-based collection
            if self.snake.pos.distance_to(c.pos) < 30.0:
                self._handle_collection(c)
                
        for p in self.collection_particles:
            p.update(self.dt)
        self.collection_particles = [p for p in self.collection_particles if p.lifetime > 0]
        
        # Camera smoothing
        self.camera.update(self.snake, self.dt)
        
        # Environmental Phenomena
        self.ambient_debris.update(self.dt)
        self.dust_current.update(self.dt, self.planets)

    def _handle_collection(self, collectible):
        # Visual feedback
        self.camera.apply_collection_feedback(self.snake.velocity)
        
        # Spawn elegant, soft particle burst
        for _ in range(8):
            angle = random.uniform(0, 360)
            speed = random.uniform(30, 80)
            vel = pygame.math.Vector2(1, 0).rotate(angle) * speed
            # Inherit slight momentum from snake
            vel += self.snake.velocity * 0.15
            lifetime = random.uniform(0.3, 0.6)
            self.collection_particles.append(CollectibleParticle(collectible.pos, vel, lifetime))
            
        # Respawn in a new orbit (potentially transferring to the other planet)
        collectible.planet = random.choice(self.planets)
        collectible.respawn()

    def draw(self):
        self.renderer.draw_background(self.screen, self.camera, self.stars)
        
        # Phenomena rendered below planets and gameplay objects
        self.renderer.draw_phenomena(self.screen, self.camera, self.ambient_debris, self.dust_current)
        
        self.renderer.draw_planets(self.screen, self.camera, self.planets)
        self.renderer.draw_collectibles(self.screen, self.camera, self.collectibles, self.collection_particles)
        self.renderer.draw_snake(self.screen, self.camera, self.snake)
        self.renderer.draw_screen_pulse(self.screen, self.camera)
        pygame.display.flip()
