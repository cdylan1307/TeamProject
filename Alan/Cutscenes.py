import pygame
import sys

<<<<<<< HEAD
=======
pygame.init()

WIDTH, HEIGHT = 1280, 720
FPS = 60

# Colors
>>>>>>> de9d295073b656f3d03ec64b0a6f99ddbdcd230a
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (218, 165, 32)
DARK_RED = (139, 0, 0)
DARK_BLUE = (25, 25, 112)
FOREST_GREEN = (34, 139, 34)

<<<<<<< HEAD
def _load_fonts():
    try:
        title_font = pygame.font.Font("../text/Oxanium-Bold.ttf", 54)
        body_font = pygame.font.Font("../text/Oxanium-Bold.ttf", 26)
        small_font = pygame.font.Font("../text/Oxanium-Bold.ttf", 20)
    except:
        title_font = pygame.font.SysFont("Arial", 54, bold=True)
        body_font = pygame.font.SysFont("Arial", 26)
        small_font = pygame.font.SysFont("Arial", 20)
    return title_font, body_font, small_font


def draw_cutscene(screen, title, lines, bg_color, title_color=GOLD, fps=60):
    title_font, body_font, small_font = _load_fonts()
    clock = pygame.time.Clock()
    width, height = screen.get_size()
=======
# Fonts
try:
    TITLE_FONT = pygame.font.Font("../text/Oxanium-Bold.ttf", 54)
    BODY_FONT = pygame.font.Font("../text/Oxanium-Bold.ttf", 26)
    SMALL_FONT = pygame.font.Font("../text/Oxanium-Bold.ttf", 20)
except:
    TITLE_FONT = pygame.font.SysFont("Arial", 54, bold=True)
    BODY_FONT = pygame.font.SysFont("Arial", 26)
    SMALL_FONT = pygame.font.SysFont("Arial", 20)


def draw_cutscene(screen, title, lines, bg_color, title_color=GOLD):
    """Draw a simple, elegant cutscene"""
    clock = pygame.time.Clock()
    fade_alpha = 255
>>>>>>> de9d295073b656f3d03ec64b0a6f99ddbdcd230a
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "continue"
                elif event.key == pygame.K_ESCAPE:
                    return "skip"
        
<<<<<<< HEAD
        screen.fill(bg_color)
 
        shadow = title_font.render(title, True, BLACK)
        screen.blit(shadow, (width // 2 - shadow.get_width() // 2 + 3, 83))
        title_surf = title_font.render(title, True, title_color)
        screen.blit(title_surf, (width // 2 - title_surf.get_width() // 2, 80))
        
        y = height // 2 - (len(lines) * 35) // 2
        for line in lines:
            text = body_font.render(line, True, WHITE)
            screen.blit(text, (width // 2 - text.get_width() // 2, y))
            y += 45
        
        prompt = small_font.render("Press SPACE to continue or ESC to skip", True, (200, 200, 200))
        screen.blit(prompt, (width // 2 - prompt.get_width() // 2, height - 50))
        
        pygame.display.flip()
        clock.tick(fps)


def level1_cutscene(screen):
=======
        # Background
        screen.fill(bg_color)
        
        # Title with shadow
        shadow = TITLE_FONT.render(title, True, BLACK)
        screen.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + 3, 83))
        title_surf = TITLE_FONT.render(title, True, title_color)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 80))
        
        # Story text
        y = HEIGHT // 2 - (len(lines) * 35) // 2
        for line in lines:
            text = BODY_FONT.render(line, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 45
        
        # Continue prompt
        prompt = SMALL_FONT.render("Press SPACE to continue or ESC to skip", True, (200, 200, 200))
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 50))
        
        # Fade in
        if fade_alpha > 0:
            fade = pygame.Surface((WIDTH, HEIGHT))
            fade.fill(BLACK)
            fade.set_alpha(int(fade_alpha))
            screen.blit(fade, (0, 0))
            fade_alpha -= 255 / (2 * FPS)
        
        pygame.display.flip()
        clock.tick(FPS)


def level1_cutscene(screen):
    """Level 1: Mount Pelion"""
>>>>>>> de9d295073b656f3d03ec64b0a6f99ddbdcd230a
    return draw_cutscene(
        screen,
        "Level 1: Mount Pelion",
        [
            "In the youth of the great warrior Achilles,",
            "he trained on Mount Pelion under the wise centaur Chiron.",
            "Alongside his companion Patroclus,",
            "Achilles learned the arts of combat and strategy.",
            "Today, his training reaches a crucial test..."
        ],
        FOREST_GREEN,
        GOLD
    )


def level2_cutscene(screen):
<<<<<<< HEAD
=======
    """Level 2: The Beach of Troy"""
>>>>>>> de9d295073b656f3d03ec64b0a6f99ddbdcd230a
    return draw_cutscene(
        screen,
        "Level 2: The Beach of Troy",
        [
            "Years have passed since Achilles' training.",
            "The Greek armies now land on the beaches of Troy,",
            "beginning the legendary Trojan War.",
            "Achilles fights at the forefront,",
            "with Patroclus ever faithful by his side."
        ],
        DARK_BLUE,
        GOLD
    )


def intermission_cutscene(screen):
<<<<<<< HEAD
=======
    """Between Level 2 and 3"""
>>>>>>> de9d295073b656f3d03ec64b0a6f99ddbdcd230a
    result = draw_cutscene(
        screen,
        "Ten Years Later...",
        [
            "Ten long years the Trojan War has raged.",
            "In his pride, Achilles refused to fight for the Greeks.",
            "To save the Greek camp from destruction,",
            "Patroclus donned Achilles' armor",
            "and went to battle in his place..."
        ],
        (30, 30, 40),
        GOLD
    )
    
    if result == "skip":
        return "skip"
    
<<<<<<< HEAD
=======
    # Part 2
>>>>>>> de9d295073b656f3d03ec64b0a6f99ddbdcd230a
    return draw_cutscene(
        screen,
        "The Fall of Patroclus",
        [
            "But fate was cruel.",
            "Hector, Prince of Troy, slew Patroclus in combat.",
            "When Achilles learned of his beloved companion's death,",
            "his grief turned to terrible rage.",
            "Now he seeks vengeance against Hector..."
        ],
        DARK_RED,
        WHITE
    )


def level3_cutscene(screen):
<<<<<<< HEAD
=======
    """Level 3: Final Duel"""
>>>>>>> de9d295073b656f3d03ec64b0a6f99ddbdcd230a
    return draw_cutscene(
        screen,
        "Level 3: The Final Duel",
        [
            "Achilles challenges Hector to single combat.",
            "The two greatest warriors face each other",
            "in a battle that will be sung of for ages.",
            "Only one will walk away...",
            "This is Achilles' vengeance."
        ],
        (50, 40, 40),
        DARK_RED
    )


def victory_cutscene(screen):
<<<<<<< HEAD
=======
    """Victory ending"""
>>>>>>> de9d295073b656f3d03ec64b0a6f99ddbdcd230a
    return draw_cutscene(
        screen,
        "Victory and Sorrow",
        [
            "Hector falls to Achilles' blade.",
            "Vengeance is won, but at what cost?",
            "Patroclus is gone, never to return.",
            "Achilles stands victorious,",
            "yet his heart remains heavy with grief."
        ],
        (40, 45, 50),
        GOLD
    )


def play_cutscene(screen, cutscene_name):
<<<<<<< HEAD
=======
    """
    Play a cutscene by name
    
    Args:
        screen: pygame display surface
        cutscene_name: "level1", "level2", "intermission", "level3", or "victory"
    
    Returns:
        "continue" or "skip"
    """
>>>>>>> de9d295073b656f3d03ec64b0a6f99ddbdcd230a
    cutscenes = {
        "level1": level1_cutscene,
        "level2": level2_cutscene,
        "intermission": intermission_cutscene,
        "level3": level3_cutscene,
        "victory": victory_cutscene
    }
    
    if cutscene_name in cutscenes:
        return cutscenes[cutscene_name](screen)
    else:
        print(f"Unknown cutscene: {cutscene_name}")
        return "skip"
<<<<<<< HEAD
=======


# Demo
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cutscenes")
    
    for name in ["level1", "level2", "intermission", "level3", "victory"]:
        if play_cutscene(screen, name) == "skip":
            break
    
    pygame.quit()


if __name__ == "__main__":
    main()
>>>>>>> de9d295073b656f3d03ec64b0a6f99ddbdcd230a
