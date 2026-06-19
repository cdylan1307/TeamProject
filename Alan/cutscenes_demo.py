import pygame
from Cutscenes import play_cutscene

def main():
    pygame.init()
    
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cutscenes Demo")
    
    # Play all cutscenes in sequence
    cutscene_order = ["level1", "level2", "intermission", "level3", "victory"]
    
    for cutscene_name in cutscene_order:
        result = play_cutscene(screen, cutscene_name)
        if result == "skip":
            print("Cutscenes skipped by user.")
            break
    
    pygame.quit()


if __name__ == "__main__":
    main()
