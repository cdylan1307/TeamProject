import pygame
from Bard import Bard

def main():
    pygame.init()

    WINDOW_WIDTH, WINDOW_HEIGHT = 1360, 720
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Bard Idle Animation Demo")

    bard = Bard(window_height=WINDOW_HEIGHT, scale=1.35)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        bard.update()

        window.fill((0, 0, 0))
        bard.draw(window)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
