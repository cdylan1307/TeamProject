import pygame
import sys
import os

pygame.init()

# --------------------
# Settings
# --------------------
WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Menu")

FPS = 60
clock = pygame.time.Clock()

# --------------------
# Font
# --------------------
FONT = pygame.font.SysFont("Courier New", 36, bold=True)
SMALL_FONT = pygame.font.SysFont("Courier New", 28, bold=True)

# --------------------
# Colors
# --------------------
BLUE = (40, 80, 160)
LIGHT_BLUE = (80, 140, 255)
GREEN = (40, 180, 80)
RED = (180, 50, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLACEHOLDER_BG = (25, 25, 35)

# --------------------
# Full Screen Shadow
# --------------------
menu_shadow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
menu_shadow.fill((0, 0, 0, 120))

# --------------------
# Load Main Background
# --------------------
background = None

if os.path.exists("jungle.jpg"):
    background = pygame.image.load("jungle.jpg").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# --------------------
# Load Settings Background
# --------------------
settings_bg = None

if os.path.exists("settings.png"):
    settings_bg = pygame.image.load("settings.png").convert()
    settings_bg = pygame.transform.scale(settings_bg, (WIDTH, HEIGHT))

# --------------------
# Load Game Background
# --------------------
game_bg = None

if os.path.exists("forest.png"):
    game_bg = pygame.image.load("forest.png").convert()
    game_bg = pygame.transform.scale(game_bg, (WIDTH, HEIGHT))

# --------------------
# Pixel Button
# --------------------
class PixelButton:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self):
        mouse = pygame.mouse.get_pos()

        color = LIGHT_BLUE if self.rect.collidepoint(mouse) else BLUE

        pygame.draw.rect(SCREEN, BLACK, self.rect.inflate(6, 6))
        pygame.draw.rect(SCREEN, color, self.rect)

        text_surface = FONT.render(self.text, False, WHITE)

        SCREEN.blit(
            text_surface,
            (
                self.rect.centerx - text_surface.get_width() // 2,
                self.rect.centery - text_surface.get_height() // 2,
            ),
        )

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and self.rect.collidepoint(event.pos)
        )

# --------------------
# Toggle Button
# --------------------
class ToggleButton:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 120, 50)
        self.enabled = True

    def draw(self):

        color = GREEN if self.enabled else RED
        text = "ON" if self.enabled else "OFF"

        pygame.draw.rect(SCREEN, BLACK, self.rect.inflate(6, 6))
        pygame.draw.rect(SCREEN, color, self.rect)

        label = SMALL_FONT.render(text, False, WHITE)

        SCREEN.blit(
            label,
            (
                self.rect.centerx - label.get_width() // 2,
                self.rect.centery - label.get_height() // 2,
            ),
        )

    def clicked(self, event):
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and self.rect.collidepoint(event.pos)
        ):
            self.enabled = not self.enabled
            return True
        return False

# --------------------
# Main Menu Buttons
# --------------------
buttons = [
    PixelButton("START", WIDTH // 2 - 100, 180, 200, 60),
    PixelButton("SETTINGS", WIDTH // 2 - 100, 260, 200, 60),
    PixelButton("CREDITS", WIDTH // 2 - 100, 340, 200, 60),
    PixelButton("QUIT", WIDTH // 2 - 100, 420, 200, 60),
]

# --------------------
# Settings Toggles
# --------------------
music_toggle = ToggleButton(550, 220)
sound_toggle = ToggleButton(550, 320)

# --------------------
# Scene Control
# --------------------
scene = "menu"
credits_y = HEIGHT
start_time = 0

transition = False
transition_progress = 0

NUM_SLICES = 20
# --------------------
# Main Loop
# --------------------
while True:

    clock.tick(FPS)

    if transition:
        transition_progress += 15

        if transition_progress >= WIDTH:
            transition = False
            transition_progress = 0
            scene = "start"
            start_time = pygame.time.get_ticks()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # --------------------
        # MENU
        # --------------------
        if scene == "menu":

            if buttons[0].clicked(event):
                transition = True
                transition_progress = 0

            elif buttons[1].clicked(event):
                scene = "settings"

            elif buttons[2].clicked(event):
                credits_y = HEIGHT
                scene = "credits"

            elif buttons[3].clicked(event):
                pygame.quit()
                sys.exit()

        # --------------------
        # START SCREEN
        # --------------------
        elif scene == "start":

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    scene = "menu"

        # --------------------
        # SETTINGS SCREEN
        # --------------------
        elif scene == "settings":

            music_toggle.clicked(event)
            sound_toggle.clicked(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    scene = "menu"

        elif scene == "credits":

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    scene = "menu"
        
        

    # ====================
    # DRAW BACKGROUND
    # ====================

    if scene == "settings":

            if settings_bg:
                SCREEN.blit(settings_bg, (0, 0))
            else:
                SCREEN.fill((40, 40, 60))

    elif scene == "start":

            if game_bg:
                SCREEN.blit(game_bg, (0, 0))
            else:
                SCREEN.fill((20, 120, 20))

    else:

        if background:
            SCREEN.blit(background, (0, 0))
        else:
            SCREEN.fill(PLACEHOLDER_BG)

    # ====================
    # MENU
    # ====================
    if scene == "menu":

        SCREEN.blit(menu_shadow, (0, 0))

        

        title = FONT.render("PIXEL GAME", False, WHITE)

        SCREEN.blit(
        title,
        (
            WIDTH // 2 - title.get_width() // 2,
            80,
        ),
        )

        for button in buttons:
            button.draw()

    # ====================
    # START
    # ====================
    elif scene == "start":

        if pygame.time.get_ticks() - start_time < 500:

            text = FONT.render("GAME STARTED!", False, WHITE)

            SCREEN.blit(
                text,
                (
                    WIDTH // 2 - text.get_width() // 2,
                    HEIGHT // 2 - text.get_height() // 2,
                ),
            )

            hint = pygame.font.SysFont(
                "Courier New",
                20
            ).render(
                "Press ESC to return to menu",
                False,
                WHITE
            )

            SCREEN.blit(
                hint,
                (
                    WIDTH // 2 - hint.get_width() // 2,
                    HEIGHT // 2 + 60,
                ),
            )

    # ====================
    # SETTINGS
    # ====================
    elif scene == "settings":

        title = FONT.render("SETTINGS", False, WHITE)

        SCREEN.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                80,
            ),
        )

        music_text = SMALL_FONT.render(
            "Music",
            False,
            WHITE
        )

        sound_text = SMALL_FONT.render(
            "Game Sounds",
            False,
            WHITE
        )

        SCREEN.blit(music_text, (180, 230))
        SCREEN.blit(sound_text, (180, 330))

        music_toggle.draw()
        sound_toggle.draw()

        hint = pygame.font.SysFont(
            "Courier New",
            20
        ).render(
            "Press ESC to return",
            False,
            WHITE
        )

        SCREEN.blit(
            hint,
            (
                WIDTH // 2 - hint.get_width() // 2,
                520,
            ),
        )

    # ====================
# CREDITS
# ====================
    elif scene == "credits":

        credits_lines = [
            "PIXEL GAME",
            "",
            "Created by Team 2",
            "",
            "Alan Haugh",
            "Dylan Mooney",
            "Cillian Lynch",
            "Jihan Xu",
        ]

        # Move credits upward
        credits_y -= 1

        line_spacing = 50

        for i, line in enumerate(credits_lines):

            text = SMALL_FONT.render(line, False, WHITE)

            SCREEN.blit(
                text,
                (
                    WIDTH // 2 - text.get_width() // 2,
                    credits_y + i * line_spacing,
                ),
            )

        # Total height of credits
        total_height = len(credits_lines) * line_spacing

        # When all text leaves screen, restart from bottom
        if credits_y + total_height < 0:
            credits_y = HEIGHT

    if transition:

    # Draw Level 1 underneath
        if game_bg:
            SCREEN.blit(game_bg, (0, 0))

        slice_width = WIDTH // NUM_SLICES

        for i in range(NUM_SLICES):

            x = i * slice_width

            slice_surface = background.subsurface(
                (x, 0, slice_width, HEIGHT)
            )

        # Alternate directions
            if i % 2 == 0:
                offset = -transition_progress
            else:
                offset = transition_progress

            SCREEN.blit(
                slice_surface,
                (x + offset, 0)
            )

    pygame.display.flip()