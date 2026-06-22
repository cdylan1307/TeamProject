import pygame
import os

class Bard:
    FRAME_DURATION = 100

    def __init__(self, window_height: int, scale: float = 1.0):
        self.frames = self._load_frames(scale)
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.x = 15
        self.y = (window_height // 2) - (self.frames[0].get_height() // 2)

    def _load_frames(self, scale: float) -> list[pygame.Surface]:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        bard_idle_path = os.path.join(base_dir, "..", "images", "Bard Idle")
        frames = []
        for i in range(3):
            frame_path = os.path.join(bard_idle_path, f"pixil-frame-{i}.png")
            frame = pygame.image.load(frame_path).convert_alpha()
            if scale != 1:
                frame = pygame.transform.scale_by(frame, scale)
            frames.append(frame)
        return frames

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.FRAME_DURATION:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time

    def draw(self, surface: pygame.Surface):
<<<<<<< HEAD
        surface.blit(self.frames[self.current_frame], (self.x, self.y))
=======
        surface.blit(self.frames[self.current_frame], (self.x, self.y))


#Main (can be moved to a separate main.py) 
if __name__ == "__main__":
    pygame.init()

    WINDOW_WIDTH, WINDOW_HEIGHT = 1360, 720
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Bard Idle Animation")

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
>>>>>>> de9d295073b656f3d03ec64b0a6f99ddbdcd230a
