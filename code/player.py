import pygame
from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer):
        super().__init__(group)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        # Initial setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']

        # Movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        # Collision
        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.collision_sprites = collision_sprites

        # Timers
        self.timers = {
            'tool use': Timer(350, self.use_tool),
            'tool switch': Timer(200),
        }

        # All inventory
        self.inventory = ['hoe', 'water', 'tomato'] 
        self.inventory_index = 0
        self.selected_tool = self.inventory[self.inventory_index]

        # Inventory
        self.item_inventory = {'tomato': 0}
        self.seed_inventory = {'tomato': 10}

        # Interaction
        self.tree_sprites = tree_sprites
        self.interaction = interaction
        self.sleep = False
        self.soil_layer = soil_layer

        # Sound
        self.watering = pygame.mixer.Sound('../audio/water.wav')
        self.watering.set_volume(0.3)

    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
        elif self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)
            self.watering.play()
        elif self.selected_tool in self.seed_inventory:
            # Plant seed if inventory allows
            if self.seed_inventory[self.selected_tool] > 0:
                self.soil_layer.plant_seed(self.target_pos, self.selected_tool)
                self.seed_inventory[self.selected_tool] -= 1

    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

    def import_assets(self):
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
            'up_action': [], 'down_action': [], 'left_action': [], 'right_action': []
        }

        for animation in self.animations.keys():
            full_path = '../graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        if not self.timers['tool use'].active and not self.sleep:
            # Vertical movements
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            # Horizontal movements
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            # Use selected tool/seed
            if mouse_buttons[0]:
                # if by bed, sleep, otherwise activate tool or whatever
                collided_interaction_sprite = pygame.sprite.spritecollide(self,self.interaction,False)
                if collided_interaction_sprite:
                    self.status = 'left_idle'
                    self.sleep = True
                else:
                    # run timer for tool use
                    self.timers['tool use'].activate()
                    self.direction = pygame.math.Vector2()
                    self.frame_index = 0

            # Change tool/seed
            if keys[pygame.K_TAB] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.inventory_index = (self.inventory_index + 1) % len(self.inventory)
                self.selected_tool = self.inventory[self.inventory_index]

    def get_status(self):
        # Action animation
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_action'
        # Idle if no movement
        elif self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    # Horizontal Collision
                    if direction == 'horizontal':
                        if self.direction.x > 0:
                            # moving right
                            self.hitbox.right = sprite.hitbox.left

                        if self.direction.x < 0:
                            # moving left
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    # Vertical Collision
                    if direction == 'vertical':
                        if self.direction.y > 0:
                            # moving down
                            self.hitbox.bottom = sprite.hitbox.top

                        if self.direction.y < 0:
                            # moving up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, dt):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        self.move(dt)
        self.animate(dt)
