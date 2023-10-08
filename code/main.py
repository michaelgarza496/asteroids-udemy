from typing import Any
import pygame
import sys

from pygame import Surface
from pygame.sprite import Group, Sprite
from pygame.math import Vector2 as V2
from pygame.mixer import Sound
from random import randint, uniform


class Laser(Sprite):
    def __init__(self, pos: tuple, *groups: Group) -> None:
        super().__init__(*groups)
        self.image = pygame.image.load("graphics/laser.png").convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.explosion_sound = Sound("sounds/explosion.wav")
        self.explosion_sound.set_volume(0.3)

        # float based position
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(0, -1)
        self.speed = 400

    def _meteor_collision(self):
        if pygame.sprite.spritecollide(
            self, meteor_group, 1, pygame.sprite.collide_mask
        ):
            self.kill()
            self.explosion_sound.play()

    def update(self):
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self._meteor_collision()
        if self.rect.bottom < 0:
            self.kill()


class Ship(Sprite):
    def __init__(self, groups) -> None:
        # 1. init parent class
        super().__init__(groups)
        # 2. Sprite needs surface (or image in Sprite class)
        self.image = pygame.image.load("graphics/ship.png").convert_alpha()
        # 3. Sprite needs a rect
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        # 4. Create mask
        self.mask = pygame.mask.from_surface(self.image)

        self.laser_sound = Sound("sounds/laser.ogg")
        self.laser_sound.set_volume(0.1)

        self.can_shoot = True
        self.shoot_time = None

    def _laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time > 500:
                self.can_shoot = True

    def _input_position(self):
        pos = pygame.mouse.get_pos()
        self.rect.center = pos

    def _laser_shoot(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
            Laser(self.rect.midtop, laser_group)
            self.laser_sound.play()

    def _meteor_collision(self):
        if pygame.sprite.spritecollide(
            self, meteor_group, True, pygame.sprite.collide_mask
        ):
            print("Your dead")

    def update(self) -> None:
        self._laser_timer()
        self._laser_shoot()
        self._input_position()
        self._meteor_collision()


class Meteor(Sprite):
    def __init__(self, pos: tuple, *groups: Group) -> None:
        super().__init__(*groups)
        self.image = self._create_meteor()
        self.original_image = self.image
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.rotation = 0.0
        self.rotation_speed = randint(400, 600)

        # float based position
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400, 600)

    def _rotate(self) -> None:
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_image, self.rotation, 1)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def _create_meteor(self) -> Surface:
        surf = pygame.image.load("graphics/meteor.png").convert_alpha()
        size = V2(surf.get_size()) * uniform(0.5, 1.5)
        return pygame.transform.scale(surf, size)

    def update(self):
        self.pos += self.direction * self.speed * dt
        self._rotate()
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()


class Score:
    def __init__(self) -> None:
        self.font = pygame.font.Font("graphics/subatomic.ttf", 50)

    def display(self):
        score_text = f"Score: {pygame.time.get_ticks() // 1000}"
        text_surf = self.font.render(score_text, True, (255, 255, 0))
        text_rect = text_surf.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 80))
        display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(
            display_surface,
            (255, 255, 255),
            text_rect.inflate(30, 30),
            width=8,
            border_radius=5,
        )


pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# background
background_surf = pygame.image.load("graphics/background.png").convert()

def create_group(all_groups: list, add_to_all_groups: bool=True) -> Group:
    g: Group = Group()
    if add_to_all_groups:
        all_groups.append(g)
    return g

# sprite groups
all_groups: list = []
spaceship_group = create_group(all_groups)
laser_group = create_group(all_groups)
meteor_group = create_group(all_groups)

# Sprite creation
ship = Ship(spaceship_group)
# Meteor((100, 100), meteor_group)

# timer
meteor_timer = pygame.event.custom_type()
pygame.time.set_timer(meteor_timer, 400)

score = Score()

# game music
music = Sound("sounds/music.wav")
music.set_volume(0.07)
music.play(loops=-1)

# game loop
while True:
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == meteor_timer:
            meteor_y = randint(-150, -50)
            meteor_x = randint(-100, WINDOW_WIDTH + 100)
            Meteor((meteor_x, meteor_y), meteor_group)

    # delta time
    dt = clock.tick() / 1000

    # background
    display_surface.blit(background_surf, (0, 0))

    # update sprites
    # spaceship_group.update()
    # laser_group.update()
    # meteor_group.update()
    for g in all_groups:
        g.update()
    for g in all_groups:
        g.draw(display_surface)
    score.display()

    # graphics
    # spaceship_group.draw(display_surface)
    # laser_group.draw(display_surface)
    # meteor_group.draw(display_surface)

    # draw the frame
    pygame.display.update()
