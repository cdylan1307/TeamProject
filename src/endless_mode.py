import pygame
import sys
import os
import math
import random
from .dealer import Dealer
from .animation_system import AnimatedPlayer, AnimatedPatroclus

WIDTH, HEIGHT = 1280, 720
MIN_Y, MAX_Y = 200, HEIGHT - 100

# Load enemy animation frames
def load_enemy_frames():
    """Load all enemy animation frames"""
    # Chiron frames
    chiron_frames = []
    for i in range(6):
        try:
            frame = pygame.image.load(f"animations/Chiron/Walking/Chiron_Walk_{i}.png").convert_alpha()
            chiron_frames.append(pygame.transform.scale_by(frame, 0.75))
        except:
            fallback = pygame.Surface((60, 60))
            fallback.fill((255, 0, 0))
            chiron_frames.append(fallback)
    
    # Archer frames
    archer_frames = []
    for i in range(1, 11):
        try:
            frame = pygame.image.load(f"sprites/ac{i}.png").convert_alpha()
            archer_frames.append(pygame.transform.scale(frame, (int(frame.get_width() * 0.55), int(frame.get_height() * 0.55))))
        except:
            fallback = pygame.Surface((45, 45))
            fallback.fill((200, 0, 0))
            archer_frames.append(fallback)
    
    # Mole frames
    mole_frames = []
    for i in range(2, 8):
        try:
            frame = pygame.image.load(f"sprites/e{i}.png").convert_alpha()
            mole_frames.append(pygame.transform.scale(frame, (int(frame.get_width() * 0.55), int(frame.get_height() * 0.55))))
        except:
            fallback = pygame.Surface((45, 45))
            fallback.fill((150, 50, 50))
            mole_frames.append(fallback)
    
    return chiron_frames, archer_frames, mole_frames


def start_endless_mode(bard, player_name="Player", game_sounds_enabled=True):
    """
    Endless mode with waves of all enemy types using proper sprites
    """
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Achilles and Patroclus - Endless Mode")
    clock = pygame.time.Clock()
    
    # Load background
    try:
        background = pygame.image.load("backgrounds/lv3background.png").convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except:
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill((40, 45, 50))
    
    # Load enemy frames
    chiron_frames, archer_frames, mole_frames = load_enemy_frames()
    
    # Load sword frames
    sword_frames = []
    for i in range(1, 4):
        try:
            frame = pygame.image.load(f"sprites/sword{i}.png").convert_alpha()
            new_size = (int(frame.get_width() * 0.6), int(frame.get_height() * 0.6))
            sword_frames.append(pygame.transform.scale(frame, new_size))
        except:
            fallback = pygame.Surface((15, 8))
            fallback.fill((255, 255, 255))
            sword_frames.append(fallback)
    
    # Fonts
    FONT = pygame.font.SysFont("Arial", 30, bold=True)
    FONT_LARGE = pygame.font.SysFont("Arial", 60, bold=True)
    
    # Player init with animated sprites
    player_x, player_y = WIDTH // 2, HEIGHT // 2
    animated_player = AnimatedPlayer(player_x, player_y, scale=1.2)
    animated_patroclus = AnimatedPatroclus(player_x - 40, player_y + 40, scale=1.0)
    
    player_health = 5
    max_health = 5
    player_coins = 100
    player_speed = 5
    
    # Sword mechanics
    is_swinging = False
    sword_frame_idx = 0
    sword_counter = 0
    sword_cooldown = 0
    SWORD_COOLDOWN = 0.5
    SWORD_ATTACK_RANGE = 95
    sword_on_right = False

    
    # Wave system
    current_wave = 1
    enemies_in_wave = 5
    enemies_killed_this_wave = 0
    wave_complete = False
    wave_notification_timer = 0
    
    # Enemy list (will spawn based on wave)
    enemies = []
    
    # Dealer
    dealer = Dealer(WIDTH - 200, 150, scale=0.5)
    shield_purchased = False
    shield_active = False
    player_inventory = []
    
    # Game state
    running = True
    game_over = False
    
    def spawn_enemy_for_wave(wave_num):
        """Spawn an enemy based on current wave"""
        enemy_types = ["chiron", "archer", "mole"]
        
        enemy_type = random.choice(enemy_types)
        spawn_x = random.choice([50, WIDTH - 50])
        spawn_y = random.randint(MIN_Y, MAX_Y)
        
        health = 5
        if enemy_type == "chiron":
            health = 9
        elif enemy_type == "archer":
            health = 5
        elif enemy_type == "mole":
            health = 3
        
        return {
            "type": enemy_type,
            "x": float(spawn_x),
            "y": float(spawn_y),
            "health": health,
            "max_health": health,
            "frame_idx": 0,
            "frame_counter": 0
        }
    
    # Spawn initial wave
    for _ in range(enemies_in_wave):
        enemies.append(spawn_enemy_for_wave(current_wave))

    
    # Main game loop
    while running:
        dt = clock.tick(60) / 1000.0
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Sword direction
                if event.key == pygame.K_d:
                    sword_on_right = True
                elif event.key == pygame.K_a:
                    sword_on_right = False
                
                # Space to acknowledge wave complete
                if event.key == pygame.K_SPACE and wave_complete:
                    wave_complete = False
                    current_wave += 1
                    enemies_killed_this_wave = 0
                    enemies_in_wave = 5 + (current_wave * 2)  # More enemies each wave
                    wave_notification_timer = 3.0  # Show "Wave X" for 3 seconds
                    
                    # Spawn new wave
                    enemies.clear()
                    for _ in range(enemies_in_wave):
                        enemies.append(spawn_enemy_for_wave(current_wave))
                
                # E key for dealer
                elif event.key == pygame.K_e:
                    if dealer.is_player_close(player_x, player_y):
                        dealer.shop_open = not dealer.shop_open
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not dealer.shop_open:  # Left click
                    if not is_swinging and sword_cooldown <= 0 and not shield_active:
                        is_swinging = True
                        sword_frame_idx = 0
                        sword_counter = 0
                        sword_cooldown = SWORD_COOLDOWN
                
                # Right click for shield
                if event.button == 3 and shield_purchased:
                    shield_active = True
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    shield_active = False

        
        # Update sword cooldown
        if sword_cooldown > 0:
            sword_cooldown -= dt
        
        # Dealer processing
        if not game_over:
            shop_action = dealer.update(player_x, player_y, False, keys, False)
            if shop_action != -1:
                chosen_item = dealer.items[shop_action]
                if player_coins >= chosen_item["cost"]:
                    player_coins -= chosen_item["cost"]
                    player_inventory.append(chosen_item["name"])
                    
                    if chosen_item["name"] == "Shield":
                        shield_purchased = True
                    elif chosen_item["name"] == "Extra Heart":
                        player_health = min(player_health + 1, max_health + 1)
                        max_health = min(max_health + 1, 6)
        
        # Update wave notification timer
        if wave_notification_timer > 0:
            wave_notification_timer -= dt
        
        # Check if wave is complete
        if enemies_killed_this_wave >= enemies_in_wave and not wave_complete and not game_over:
            wave_complete = True
        
        # Player movement
        if not wave_complete and not game_over and not dealer.shop_open:
            if keys[pygame.K_w]: player_y -= player_speed
            if keys[pygame.K_s]: player_y += player_speed
            if keys[pygame.K_a]: player_x -= player_speed
            if keys[pygame.K_d]: player_x += player_speed
            
            player_x = max(0, min(WIDTH, player_x))
            player_y = max(MIN_Y, min(MAX_Y, player_y))
            
            # Update animated player
            animated_player.x = player_x
            animated_player.y = player_y
            animated_player.update_movement(keys)
            animated_player.update()
            
            # Update Patroclus
            animated_patroclus.follow_player(player_x - 40, player_y + 40)
            healing_result = animated_patroclus.update()
            if healing_result == "healing_complete":
                player_health = min(player_health + 1, max_health)

        
        # Enemy AI and animation
        if not wave_complete and not game_over:
            for enemy in enemies:
                # Update animation
                enemy["frame_counter"] += 1
                if enemy["frame_counter"] >= 4:
                    enemy["frame_counter"] = 0
                    if enemy["type"] == "chiron":
                        enemy["frame_idx"] = (enemy["frame_idx"] + 1) % len(chiron_frames)
                    elif enemy["type"] == "archer":
                        enemy["frame_idx"] = (enemy["frame_idx"] + 1) % len(archer_frames)
                    elif enemy["type"] == "mole":
                        enemy["frame_idx"] = (enemy["frame_idx"] + 1) % len(mole_frames)
                
                # Move toward player
                dx = player_x - enemy["x"]
                dy = player_y - enemy["y"]
                dist = math.hypot(dx, dy)
                if dist > 50:
                    speed = 2 if enemy["type"] != "mole" else 3
                    enemy["x"] += (dx / dist) * speed
                    enemy["y"] += (dy / dist) * speed
                elif dist < 40:
                    # Enemy attacks player
                    player_health -= 0.5 * dt  # Gradual damage
        
        # Sword attack
        if is_swinging and not dealer.shop_open:
            sword_counter += 1
            if sword_counter >= 4:
                sword_counter = 0
                sword_frame_idx += 1
                if sword_frame_idx >= len(sword_frames):
                    is_swinging = False
                    sword_frame_idx = 0
                    
                    # Check hits
                    player_rect = animated_player.get_rect()
                    for enemy in enemies[:]:
                        dist = math.hypot(player_rect.centerx - enemy["x"], player_rect.centery - enemy["y"])
                        if dist <= SWORD_ATTACK_RANGE:
                            enemy["health"] -= 1
                            if enemy["health"] <= 0:
                                enemies.remove(enemy)
                                enemies_killed_this_wave += 1
                                player_coins += 10
                            break
        
        if player_health <= 0:
            game_over = True

        
        # Rendering
        screen.blit(background, (0, 0))
        
        # Draw enemies with proper sprites
        for enemy in enemies:
            if enemy["type"] == "chiron":
                frame = chiron_frames[enemy["frame_idx"]]
            elif enemy["type"] == "archer":
                frame = archer_frames[enemy["frame_idx"]]
            elif enemy["type"] == "mole":
                frame = mole_frames[enemy["frame_idx"]]
            else:
                frame = pygame.Surface((40, 40))
                frame.fill((255, 0, 0))
            
            enemy_rect = frame.get_rect(center=(int(enemy["x"]), int(enemy["y"])))
            screen.blit(frame, enemy_rect)
            
            # Health bar
            if enemy["health"] < enemy["max_health"]:
                bar_width = 50
                bar_height = 6
                health_ratio = enemy["health"] / enemy["max_health"]
                pygame.draw.rect(screen, (0, 0, 0), (enemy["x"] - bar_width//2 - 1, enemy["y"] - 35 - 1, bar_width + 2, bar_height + 2))
                pygame.draw.rect(screen, (180, 50, 50), (enemy["x"] - bar_width//2, enemy["y"] - 35, bar_width, bar_height))
                pygame.draw.rect(screen, (40, 180, 80), (enemy["x"] - bar_width//2, enemy["y"] - 35, bar_width * health_ratio, bar_height))
        
        # Draw dealer
        dealer.draw(screen, player_x, player_y, player_coins)
        
        # Draw player and sword (only when shop closed)
        if not dealer.shop_open:
            animated_player.draw(screen)
            animated_patroclus.draw(screen)
            
            # Draw sword
            if is_swinging:
                raw_sword = sword_frames[sword_frame_idx]
                current_sword_img = pygame.transform.flip(raw_sword, True, False) if sword_on_right else raw_sword
                offset_x = 10 if sword_on_right else -10
                player_rect = animated_player.get_rect()
                sword_draw_rect = current_sword_img.get_rect(center=(int(player_rect.centerx + offset_x), int(player_rect.centery)))
                screen.blit(current_sword_img, sword_draw_rect)
            
            # Draw shield
            if shield_active:
                player_rect = animated_player.get_rect()
                shield_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(shield_surf, (100, 150, 255, 80), (60, 60), 60)
                pygame.draw.circle(shield_surf, (150, 200, 255, 120), (60, 60), 60, 3)
                screen.blit(shield_surf, (player_rect.centerx - 60, player_rect.centery - 60))
        
        # Draw bard
        if bard:
            bard.update()
            bard.draw(screen)

        
        # Draw HUD
        wave_text = FONT.render(f"Wave: {current_wave}", True, (255, 255, 255))
        screen.blit(wave_text, (20, 20))
        
        kills_text = FONT.render(f"Kills: {enemies_killed_this_wave} / {enemies_in_wave}", True, (255, 255, 255))
        screen.blit(kills_text, (20, 60))
        
        coins_text = FONT.render(f"Coins: {player_coins}", True, (255, 215, 0))
        screen.blit(coins_text, (20, 100))
        
        # Health bar
        health_text = FONT.render(f"HP: {int(player_health)}/{max_health}", True, (255, 50, 50))
        screen.blit(health_text, (20, 140))
        
        # Wave notification
        if wave_notification_timer > 0:
            wave_notif = FONT_LARGE.render(f"WAVE {current_wave}", True, (255, 215, 0))
            screen.blit(wave_notif, (WIDTH // 2 - wave_notif.get_width() // 2, 100))
        
        # Wave complete message
        if wave_complete and not game_over:
            complete_text = FONT_LARGE.render("WAVE COMPLETE!", True, (0, 255, 0))
            screen.blit(complete_text, (WIDTH // 2 - complete_text.get_width() // 2, HEIGHT // 2 - 50))
            
            continue_text = FONT.render("Press SPACE for next wave", True, (255, 255, 255))
            screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 20))
        
        # Game over screen
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_text = FONT_LARGE.render("GAME OVER", True, (255, 50, 50))
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
            
            final_wave_text = FONT.render(f"{player_name} reached Wave {current_wave}", True, (255, 255, 255))
            screen.blit(final_wave_text, (WIDTH // 2 - final_wave_text.get_width() // 2, HEIGHT // 2 - 20))
            
            exit_text = FONT.render("Press ESC to return to menu", True, (200, 200, 200))
            screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 40))
            
            # Save to endless leaderboard
            save_endless_score(player_name, current_wave)
        
        pygame.display.flip()
    
    pygame.quit()

def save_endless_score(player_name, wave):
    """Save endless mode score to separate leaderboard"""
    import json
    leaderboard_file = "endless_leaderboard.json"
    
    try:
        with open(leaderboard_file, 'r') as f:
            leaderboard = json.load(f)
    except:
        leaderboard = []
    
    leaderboard.append({"name": player_name, "wave": wave})
    leaderboard.sort(key=lambda x: x["wave"], reverse=True)
    leaderboard = leaderboard[:10]  # Keep top 10
    
    with open(leaderboard_file, 'w') as f:
        json.dump(leaderboard, f)
