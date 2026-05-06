import sys
import pygame
from src.game import Game

def main():
    # Initialize all imported pygame modules
    pygame.init()
    
    # Create the core game instance and run the loop
    game = Game()
    game.run()
    
    # Gracefully exit when the loop terminates
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
