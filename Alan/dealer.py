import pygame
import os

class Dealer:
    def __init__(self, x: int, y: int, scale: float = 0.5):

        base_dir = os.path.dirname(os.path.abspath(__file__))
        dealer_path = os.path.join(base_dir, "..", "images", "Dealer.png")
        self.image = pygame.image.load(dealer_path).convert_alpha()
        if scale != 1.0:
            self.image = pygame.transform.scale_by(self.image, scale)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.shop_open = False
        self.interaction_distance = 100
        self.selected_item = 0
        
        #CUSTOMIZABLE ITEMS
        self.items = [
            {"name": "Battle Axe", "color": (255, 0, 0), "cost": 15, "image": "images/axeattack/pixil-frame-0 (4).png"},
            {"name": "Sword", "color": (0, 0, 255), "cost": 15, "image": "images/swordattack/pixil-frame-0.png"},
            {"name": "Spear", "color": (200, 200, 0), "cost": 15, "image": "images/spearattack/pixil-frame-0.png"},
            {"name": "Colosseum Ticket", "color": (0, 255, 0), "cost": 15, "image": "images/colosseumticket.png"}
        ]
        
        self._load_item_images()
        self.font_large = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 24)
        
    def _load_item_images(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for item in self.items:
            if item["image"]:
                try:
                    path = os.path.join(base_dir, "..", item["image"])
                    item["loaded_image"] = pygame.transform.scale(
                        pygame.image.load(path).convert_alpha(), (100, 100))
                except:
                    item["loaded_image"] = None
            else:
                item["loaded_image"] = None
    
    def is_player_close(self, player_x: int, player_y: int) -> bool:
        #Checks if the player is within interaction distance#
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery
        return (dx * dx + dy * dy) ** 0.5 <= self.interaction_distance
    
    def update(self, player_x: int, player_y: int, e_pressed: bool, keys, enter_pressed) -> int:
        if e_pressed and self.is_player_close(player_x, player_y):
            self.shop_open = not self.shop_open
        
        if self.shop_open:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.selected_item = (self.selected_item - 1) % len(self.items)
                pygame.time.wait(150)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.selected_item = (self.selected_item + 1) % len(self.items)
                pygame.time.wait(150)
            if enter_pressed:
                return self.selected_item
        
        return -1
    
    def buy_item(self, item_index: int, player_health: int) -> tuple[int, str]:
        item = self.items[item_index]
        return player_health - item["cost"], item["name"]
    
    def draw(self, surface: pygame.Surface, player_x: int, player_y: int, player_health: int):
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
            self._draw_shop(surface, player_health)
    
    def _draw_shop(self, surface: pygame.Surface, player_health: int):
        sw, sh = surface.get_size()
        mw, mh = 600, 500
        mx, my = (sw - mw) // 2, (sh - mh) // 2
        
        pygame.draw.rect(surface, (50, 50, 50), (mx, my, mw, mh))
        pygame.draw.rect(surface, (200, 150, 50), (mx, my, mw, mh), 5)
    
        title = self.font_large.render("DEALER'S SHOP", True, (255, 255, 255))
        surface.blit(title, (mx + (mw - title.get_width()) // 2, my + 20))
        health = self.font_small.render(f"Your Health: {player_health}", True, (255, 100, 100))
        surface.blit(health, (mx + 20, my + 70))
        
        item_spacing = 250
        grid_width = 2 * item_spacing
        start_x = mx + (mw - grid_width) // 2 + 50
        
        for i, item in enumerate(self.items):
            row, col = i // 2, i % 2
            ix = start_x + col * item_spacing
            iy = my + 120 + row * 180
            
            if i == self.selected_item:
                pygame.draw.rect(surface, (255, 255, 0), (ix - 10, iy - 10, 120, 120), 4)
            
            if item["loaded_image"]:
                surface.blit(item["loaded_image"], (ix, iy))
            else:
                pygame.draw.rect(surface, item["color"], (ix, iy, 100, 100))
                pygame.draw.rect(surface, (255, 255, 255), (ix, iy, 100, 100), 2)
            
            name = self.font_small.render(item["name"], True, (255, 255, 255))
            surface.blit(name, (ix + 50 - name.get_width() // 2, iy + 110))
            cost = self.font_small.render(f"Cost: {item['cost']} HP", True, (255, 200, 100))
            surface.blit(cost, (ix + 50 - cost.get_width() // 2, iy + 135))
        
        instruction_text = "W/S Select   |   ENTER Buy   |   E Close"
        text = self.font_small.render(instruction_text, True, (200, 200, 200))
        surface.blit(text, (mx + (mw - text.get_width()) // 2, my + mh - 30))
