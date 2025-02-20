from random import randint, uniform
import pygame
from os.path import join #join file folder in the correct way for each OS


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.original_image = pygame.image.load(join('images', 'player.png')).convert_alpha() #convert optimizes the image
        self.image = self.original_image
        self.rect = self.image.get_frect(center = (window_width/2, window_height/1.5))
        self.direction = pygame.Vector2()
        self.speed = 300
        self.rotation = 0
        self.mask = pygame.mask.from_surface(self.image)

        #cooldown
        self.can_shoot = True
        self.shoot_time = 0
        self.shoot_cooldown = 600

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.shoot_cooldown:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        justKeys = pygame.key.get_just_pressed()

        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])

        # normalize sets a limit for the max length of the vector making diagonal movement have the same speed as linear movement | a vector returns false if x and y are 0 and True otherwise
        self.direction = self.direction.normalize() if self.direction else self.direction

        self.rect.center += self.direction * self.speed * dt

        if justKeys[pygame.K_SPACE] and player.can_shoot:
            Laser((all_sprites, laser_sprites), laser_surf, self.rect.midtop)
            player.can_shoot = False
            player.shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf, posX, posY):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (posX, posY))

class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        self.speed = 1000

    def update(self, dt):
        self.rect.y -= self.speed *dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.original_image = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = 0
        self.life_time = 3000
        self.speed = 400
        self.rotation = 0.1
        self.rotation_speed = randint(20, 100)
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)

    def meteor_timer(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.life_time:
            self.kill()

    def update(self, dt):
        self.meteor_timer()
        self.rect.center += self.direction * self.speed * dt

        #rotation
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, groups, surfs, pos):
        super().__init__(groups)
        self.surfs = surfs
        self.current_img_index = 0
        self.image = self.surfs[0]
        self.rect = self.image.get_frect(center = pos)
        self.animation_speed = 20


    def update(self, dt):
        if self.current_img_index + self.animation_speed * dt < len(self.surfs):
            self.current_img_index += self.animation_speed * dt
            self.image = self.surfs[int(self.current_img_index)]
            self.rect = self.image.get_frect(center = self.rect.center)
        else:
            self.kill()


def collisions():
    global running #makes the variable global

    if pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask): # dokill only kills the sprite in the next frame | mask are really heavy so we shouldn't abuse them
        running = False

    for laser in laser_sprites:
        meteor_collision = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if meteor_collision:
            AnimatedExplosion(all_sprites, animated_explosion_surfs, meteor_collision[0].rect.center)
            explosion_sound.play()
            laser.kill()

def display_score():
    current_time = pygame.time.get_ticks()
    text_surf = font.render(str(current_time), True, (240, 230, 240))
    text_rect = text_surf.get_frect(midbottom = (window_width/2, window_height-50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240, 230, 240),text_rect.inflate(20, 10).move(0, -7), 2, 8, )

#general setup
pygame.init()
window_width, window_height = 1280, 720
display_surface = pygame.display.set_mode((window_width, window_height)) # creates a blank window
pygame.display.set_caption("SpaceShooter")


#import
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png'))
laser_surf = pygame.image.load(join("images", 'laser.png'))
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
animated_explosion_surfs = list()
animated_explosion_surfs = [pygame.image.load(join('images', 'explosion', f'{i}.png')) for i in range(21)]
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.2)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.2)
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.1)
game_music.play(loops = -1)
#sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

for i in range(20):
    ranX, ranY = randint(0, window_width), randint(0, window_height)
    star = Star(all_sprites, star_surf, ranX, ranY)

player = Player(all_sprites)

#meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500) #creates a timer for the event to happen

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick() / 1000 #clock.tick returns the miliseconds that each computer took to load each frame

    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            ranX, ranY = randint(50, window_width-50), randint(-300, -100)
            meteor = Meteor((all_sprites, meteor_sprites), meteor_surf, (ranX, ranY))
            meteor.start_time = pygame.time.get_ticks()

    #update
    all_sprites.update(dt)
    collisions()

    #draw the game
    display_surface.fill((50, 40, 60))
    display_score()
    all_sprites.draw(display_surface)

    pygame.display.update() #updates the screen

pygame.quit()