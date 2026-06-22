import pygame
import sys

pygame.init()

# Screen
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Load attack animation
attack_frames = []
for i in range(1, 11):
    attack_frames.append(
        pygame.image.load(f"ac{i}.png").convert_alpha()
    )

# Load projectile image
projectile_img = pygame.image.load("arrow.png").convert_alpha()

# Enemy position
enemy_x = 200
enemy_y = 500

# Animation
current_frame = 0
frame_delay = 4
frame_counter = 0

# Projectile data
projectiles = []
projectile_speed = 25

# Prevent spawning multiple projectiles
projectile_spawned = False

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -------------------
    # Attack Animation
    # -------------------
    frame_counter += 1

    if frame_counter >= frame_delay:
        frame_counter = 0

        current_frame += 1

        if current_frame == 9 and not projectile_spawned:
                projectile_spawned = True

                projectiles.append({
                    "x": enemy_x + 80,
                    "y": enemy_y + 30
                })

        if current_frame >= len(attack_frames):
            current_frame = 0
            projectile_spawned = False

        # When animation reaches ac10
        

    # -------------------
    # Projectile Movement
    # -------------------
    for projectile in projectiles:
        projectile["x"] += projectile_speed

    projectiles = [
        p for p in projectiles
        if p["x"] < WIDTH
]

    # -------------------
    # Draw
    # -------------------
    screen.fill((30, 30, 30))

    # Draw enemy animation
    enemy_image = attack_frames[current_frame]
    enemy_rect = enemy_image.get_rect(center=(enemy_x, enemy_y))
    screen.blit(enemy_image, enemy_rect)

    # Draw projectile
    for projectile in projectiles:
        projectile_rect = projectile_img.get_rect(
            center=(projectile["x"], projectile["y"])
        )
        screen.blit(projectile_img, projectile_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()