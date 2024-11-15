import pygame
from settings import *

class Overlay:
    def __init__(self, player):
        # General setup
        self.display_surface = pygame.display.get_surface()
        self.player = player

        overlay_path = '../graphics/overlay/'
        self.items_surf = {item: pygame.image.load(f'{overlay_path}{item}.png').convert_alpha() 
                           for item in player.inventory}

    def display(self):
        # Display selected tool or seed
        selected_item = self.player.selected_tool if self.player.selected_tool else self.player.selected_seed
        item_surf = self.items_surf[selected_item]
        item_rect = item_surf.get_rect(midbottom=OVERLAY_POSITIONS['tool'])  # Use single position
        self.display_surface.blit(item_surf, item_rect)