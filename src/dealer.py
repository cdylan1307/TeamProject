import pygame
import os
import sys

class Dealer:
    def __init__(self, x: int, y: int, scale: float = 0.5):
        # Handle both executable and script environments
        if getattr(sys, 'frozen', False):
            # Running as executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        dealer_path = os.path.join(base_dir, "images", "Dealer.png")
        if not os.path.exists(dealer_path):
            dealer_path = os.path.join(base_dir, "..", "images", "Dealer.png")

        try:
            self.image = pygame.image.load(dealer_path).convert_alpha()
            if scale != 1.0:
                self.image = pygame.transform.scale_by(self.image, scale)
        except FileNotFoundError:
            self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (139, 69, 19), (0, 0, 100, 100))
            pygame.draw.rect(self.image, (212, 175, 55), (10, 10, 80, 80), 5)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.shop_open = False
        self.interaction_distance = 100
        self.selected_item = 0
        
        self.mw, self.mh = 1280, 720
        
        self.items = [
            {"name": "Shield", "color": (100, 150, 255), "cost": 100, "image": None},  # Blue shield will be drawn
            {"name": "Extra Heart", "color": (255, 50, 50), "cost": 50, "image": None},  # Heart will be drawn
            {"name": "Spear", "color": (200, 200, 0), "cost": 15, "image": "images/spearattack/pixil-frame-0.png"},
            {"name": "Colosseum Ticket", "color": (0, 255, 0), "cost": 15, "image": "images/colosseumticket.png"}
        ]
        
        self._load_item_images()
        self.font_large = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 24, bold=True)
        
    def _load_item_images(self):
        # Handle both executable and script environments
        if getattr(sys, 'frozen', False):
            # Running as executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        for item in self.items:
            if item["image"]:
                try:
                    path = os.path.join(base_dir, item["image"])
                    if not os.path.exists(path):
                        path = os.path.join(base_dir, "..", item["image"])
                    item["loaded_image"] = pygame.transform.scale(
                        pygame.image.load(path).convert_alpha(), (120, 120))
                except:
                    item["loaded_image"] = None
            else:
                item["loaded_image"] = None
    
    def is_player_close(self, player_x: int, player_y: int) -> bool:
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery
        return (dx * dx + dy * dy) ** 0.5 <= self.interaction_distance
    
    def update(self, player_x: int, player_y: int, e_pressed: bool, keys, enter_pressed) -> int:
        if e_pressed and self.is_player_close(player_x, player_y):
            self.shop_open = not self.shop_open
        
        if self.shop_open:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.selected_item = (self.selected_item - 1) % len(self.items)
                pygame.time.wait(150)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.selected_item = (self.selected_item + 1) % len(self.items)
                pygame.time.wait(150)
                
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.selected_item = (self.selected_item - 4) % len(self.items)
                pygame.time.wait(150)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.selected_item = (self.selected_item + 4) % len(self.items)
                pygame.time.wait(150)
                
            if enter_pressed:
                return self.selected_item
        
        return -1
    
    def buy_item(self, item_index: int, player_coins: int) -> tuple[int, str]:
        item = self.items[item_index]
        if player_coins >= item["cost"]:
            return player_coins - item["cost"], item["name"]
        return player_coins, "INSUFFICIENT_FUNDS"
    
    def draw(self, surface: pygame.Surface, player_x: int, player_y: int, player_coins: int):
        surface.blit(self.image, self.rect)
        
        if self.is_player_close(player_x, player_y) and not self.shop_open:
            text = self.font_small.render("Press E to shop", True, (255, 255, 255))
            bg = pygame.Surface((text.get_width() + 20, text.get_height() + 10))
            bg.fill((0, 0, 0))
            bg.set_alpha(180)
            x = self.rect.centerx - text.get_width() // 2 - 10
            y = self.rect.top - 40
            surface.blit(bg, (x, y))
            surface.blit(text, (x + 10, y + 5))
        
        if self.shop_open:
            self._draw_shop(surface, player_coins)
    
    def _draw_shop(self, surface: pygame.Surface, player_coins: int):
        mx, my = 0, 0
        
        shop_bg = pygame.Surface((self.mw, self.mh))
        shop_bg.fill((20, 20, 25)) 
        surface.blit(shop_bg, (mx, my))
        
        pygame.draw.rect(surface, (200, 150, 50), (mx, my, self.mw, self.mh), 8)
    
        title = self.font_large.render("DEALER'S SHOP", True, (255, 255, 255))
        surface.blit(title, (mx + (self.mw - title.get_width()) // 2, my + 40))
        
        coins_hud = self.font_small.render(f"Your Coins: {player_coins}", True, (255, 215, 0))
        surface.blit(coins_hud, (mx + 180, my + 60))
        
        item_spacing = 280
        start_x = mx + (self.mw - (len(self.items) * item_spacing)) // 2 + 80
        item_y = my + 260
        
        for i, item in enumerate(self.items):
            ix = start_x + i * item_spacing
            
            if i == self.selected_item:
                pygame.draw.rect(surface, (255, 255, 0), (ix - 15, item_y - 15, 150, 150), 5, border_radius=8)
            else:
                pygame.draw.rect(surface, (60, 60, 65), (ix - 15, item_y - 15, 150, 150), 2, border_radius=8)
            
            if item["loaded_image"]:
                surface.blit(item["loaded_image"], (ix, item_y))
            elif item["name"] == "Shield":
                # Draw a blue shield bubble icon
                shield_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                # Draw main shield bubble
                pygame.draw.circle(shield_surface, (100, 150, 255, 200), (60, 60), 50)
                # Draw shield border
                pygame.draw.circle(shield_surface, (150, 200, 255), (60, 60), 50, 4)
                # Draw inner highlight
                pygame.draw.circle(shield_surface, (180, 220, 255, 150), (50, 50), 20)
                surface.blit(shield_surface, (ix, item_y))
            elif item["name"] == "Extra Heart":
                # Draw a custom heart icon
                heart_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                # Draw heart shape
                heart_color = (255, 40, 60)
                pygame.draw.circle(heart_surface, heart_color, (40, 40), 30)
                pygame.draw.circle(heart_surface, heart_color, (80, 40), 30)
                heart_points = [(20, 40), (110, 40), (60, 100)]
                pygame.draw.polygon(heart_surface, heart_color, heart_points)
                surface.blit(heart_surface, (ix, item_y))
            else:
                pygame.draw.rect(surface, item["color"], (ix, item_y, 120, 120), border_radius=4)
                pygame.draw.rect(surface, (255, 255, 255), (ix, item_y, 120, 120), 2, border_radius=4)
            
            name = self.font_small.render(item["name"], True, (255, 255, 255))
            surface.blit(name, (ix + 60 - name.get_width() // 2, item_y + 150))
            
            cost = self.font_small.render(f"Cost: {item['cost']} Coins", True, (255, 200, 100))
            surface.blit(cost, (ix + 60 - cost.get_width() // 2, item_y + 185))
        
        instruction_text = "WASD / ARROWS Select   |   ENTER Buy   |   E Close"
        text = self.font_small.render(instruction_text, True, (200, 200, 200))
        surface.blit(text, (mx + (self.mw - text.get_width()) // 2, my + self.mh - 50))