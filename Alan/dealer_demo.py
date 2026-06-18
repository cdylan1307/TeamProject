import pygame
import os
from dealer import Dealer

# Example usage and demo for the Dealer class
if __name__ == "__main__":
    pygame.init()
    
    WINDOW_WIDTH, WINDOW_HEIGHT = 1360, 720
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Dealer Shop Demo")
    
    # Create dealer at center of screen
    dealer = Dealer(x=WINDOW_WIDTH // 2 - 50, y=WINDOW_HEIGHT // 2 - 50, scale=1.5)
    
    # Simple player setup
    player_x, player_y = 100, 100
    player_health = 100
    player_speed = 5
    
    # Load player image
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        player_img = pygame.transform.scale(
            pygame.image.load(os.path.join(base_dir, "..", "images", "player.png")).convert_alpha(),
            (50, 50))
    except:
        # Create a simple colored square if player image not found
        player_img = pygame.Surface((50, 50))
        player_img.fill((0, 255, 0))
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        e_pressed = enter_pressed = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    e_pressed = True
                elif event.key == pygame.K_RETURN:
                    enter_pressed = True
        
        # Player movement (only when shop is closed)
        if not dealer.shop_open:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_x += player_speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player_y -= player_speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                player_y += player_speed
        
        # Update dealer and handle purchase
        keys = pygame.key.get_pressed()
        selected = dealer.update(player_x, player_y, e_pressed, keys, enter_pressed)
        
        if selected >= 0:
            player_health, item_name = dealer.buy_item(selected, player_health)
            print(f"Purchased {item_name}! Health: {player_health}")
        
        # Draw everything
        window.fill((139, 69, 19))  # Brown background
        dealer.draw(window, player_x, player_y, player_health)
        window.blit(player_img, (player_x, player_y))
        
        # Draw player health on screen
        health_text = pygame.font.Font(None, 36).render(f"Health: {player_health}", True, (255, 255, 255))
        window.blit(health_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
