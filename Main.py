import pygame
from pygame import *
from pygame.locals import *
import random


pygame.init()

# le music and le soundes >:^)
pygame.mixer.music.load('audio/ambiance.wav')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)

shot_sound = pygame.mixer.Sound('audio/shot.mp3')
recharged_sound = pygame.mixer.Sound('audio/recharged.wav')
insanity_whispering_sound = pygame.mixer.Sound('audio/Insanity_Whispers.mp3')
insanity_ambient_sound = pygame.mixer.Sound('audio/low_sanity_ambient.wav')
insanity_ambient_sound.set_volume(0)

CH1 = pygame.mixer.Channel(1)
CH2 = pygame.mixer.Channel(2)

r_s1 = pygame.mixer.Sound('audio/r1_sound.wav')
r_s2 = pygame.mixer.Sound('audio/r2_sound.wav')
r_s3 = pygame.mixer.Sound('audio/r3_sound.wav')
r_s4 = pygame.mixer.Sound('audio/r4_sound.wav')
r_s5 = pygame.mixer.Sound('audio/r5_sound.wav')
r_s6 = pygame.mixer.Sound('audio/r6_sound.wav')
recharging_sounds = [r_s1, r_s2, r_s3, r_s4, r_s5, r_s6]

bullet_charged_sound = pygame.mixer.Sound('audio/bullet_charged.wav')
out_of_ammo_sound = pygame.mixer.Sound('audio/out_of_ammo.wav')

# create the window
game_width = 900
game_height = 500
screen_size = (game_width, game_height)
game_window = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Night Sky: Field')

info = display.Info()
FULLSCREEN_SIZE = (info.current_w, info.current_h)
is_fullscreen = False

screen = display.set_mode((game_width, game_height), RESIZABLE)
current_size = screen.get_size()
last_size = current_size


# load images
images = {}
def load_image(name, filename, flip_x = False):
    images[name] = pygame.image.load(filename).convert_alpha()

    # flip image on the x-axis
    if flip_x:
        images[name] = pygame.transform.flip(images[name], True, False)

load_image('bg', 'images/bg_blue.png')
load_image('table', 'images/bg_wood.png')
load_image('shadow', 'images/shadow_enemy.png')
load_image('crosshair', 'images/crosshair_outline_small.png')
load_image('crosshair_charged', 'images/crosshair_charged.png')
load_image('bullet', 'images/icon_bullet_silver_long.png')
load_image('score', 'images/text_score_small.png')
load_image('special_points', 'images/special_points_text.png')
load_image('colon', 'images/text_dots_small.png')
load_image('slash', 'images/slash_text.png')
load_image('recharge', 'images/text_recharge.png')
load_image('charged', 'images/text_charged.png')
load_image('uncharged', 'images/text_uncharged.png')
load_image('status', 'images/status.png')
load_image('low_sanity', 'images/low_sanity.png')
load_image('icon', 'images/icon.png')

pygame.display.set_icon(images['icon'])

crosshair_charged = pygame.image.load('images/crosshair_charged.png')
status_screen = pygame.image.load('images/status.png')
low_sanity_indication = pygame.image.load('images/low_sanity.png')

# load the number images
for i in range(10):
    load_image(str(i), f'images/text_{i}_small.png')

# function for displaying the current score
def display_score():
    game_window.blit(images['score'], (5, 5))
    game_window.blit(images['colon'], (5 + images['score'].get_width(), 5))

    digit_x = images['score'].get_width() + images['colon'].get_width() + 20
    for digit in str(score):
        game_window.blit(images[digit], (digit_x, 5))
        digit_x += 25

class SanityBar():
    def __init__(self, x, y, w, h, max_sanity):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.sanity = max_sanity
        self.max_sanity = max_sanity

    def draw(self, surface):
        #calculate sanity ratio
        ratio = self.sanity / self.max_sanity
        pygame.draw.rect(surface, "black", (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, "white", (self.x, self.y, self.w * ratio, self.h))


class enemy(pygame.sprite.Sprite):

    def __init__(self, x, y):

        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.x += random.randint(0, 85) * 10
        self.y += random.randint(0, 20) * 10

        # keep track of whether this enemy has been hit or not
        self.is_hit = False

    def draw(self):

        # draw the enemy if it hasn't been hit yet
        if self.is_hit == False:
            game_window.blit(self.image, (self.x, self.y))


class Shadow(enemy):

    def __init__(self, x):

        super().__init__(x, game_height - 450)
        self.points = random.choice([1, 2])
        self.special_points = 1
        self.image = images['shadow']

    def update(self):
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

# sprite groups
shadow_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()





# game variables
score = 0
special_points = 0
special_points_left = 25
bullet_charged = True
enemy_max_count = 10
current_enemies_count = 0

sanity_decreasing = 0
sanity_decreasing_total = 0
max_spawnrate = 3

# stats!
remaining_bullets = 4
bullets_per_clip = 4
recharging_delay = 1000
bullet_charge_delay = 850
bcd_after_sound = 400
recoil = 50
damage = 1
###aim_max_shifting = 10

sanity_bar = SanityBar(game_width - 880, game_height - 8, 565, 5, 100) #НАДА
sanity_bar.sanity = 100
ls_opacity = 0


def new_game():

    # hide the mouse cursor
    pygame.mouse.set_visible(False)

    shadow_group.empty()
    all_sprites.empty()
    crosshair_charged.set_alpha(255)

new_game()

# game loop
clock = pygame.time.Clock()
fps = 60
running = True
recharging_procces = False
status_screen_hovering = False

BULLET_CHARGE_EVENT = pygame.USEREVENT + 1
BDE_AFTER_SOUND = pygame.USEREVENT + 2
RECHARGING_EVENT = pygame.USEREVENT + 3

# statuses opacity
recharge_text = pygame.image.load('images/text_recharge.png')
recharge_text.set_alpha(0)
charged_text = pygame.image.load('images/text_charged.png')
charged_text.set_alpha(255)
uncharged_text = pygame.image.load('images/text_uncharged.png')
uncharged_text.set_alpha(0)
low_sanity_indication.set_alpha(0)

while running:

    clock.tick(fps)

    if current_enemies_count != 0:
        sanity_decreasing_total = ((sanity_decreasing * current_enemies_count) / (current_enemies_count * 10)) / 25

    else:
        sanity_decreasing_total = 0

##########SOME#SOUNDS#############
    if not CH1.get_busy():
        CH1.play(insanity_whispering_sound)

    if not CH2.get_busy():
        CH2.play(insanity_ambient_sound)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False



#############SHOOTING#AND#AMMO#################################
        # detect mouse click
        if event.type == MOUSEBUTTONDOWN:

            if remaining_bullets != 0 and bullet_charged and not status_screen_hovering:
                shot_sound.play()
                x, y = mouse.get_pos()
                mouse.set_pos(x, y - recoil)
                remaining_bullets -= 1
                bullet_charged = False

                # change crosshair to uncharged type
                crosshair_charged.set_alpha(0)


                # coordinates of the mouse click
                click_x, click_y = event.pos

                # check if an enemy was hit
                for sprite in all_sprites:
                    if sprite.is_hit == False and sprite.rect.collidepoint(click_x, click_y):
                        sprite.is_hit = True
                        current_enemies_count -= 1
                        sanity_decreasing -= 1
                        score += sprite.points
                        break

                if remaining_bullets != 0:
                    pygame.time.set_timer(BULLET_CHARGE_EVENT, bullet_charge_delay, True)

            elif remaining_bullets == 0 and not status_screen_hovering:
                out_of_ammo_sound.play()


        if event.type == BULLET_CHARGE_EVENT:
            bullet_charged_sound.play()
            pygame.time.set_timer(BDE_AFTER_SOUND, bcd_after_sound, True)

            #change crosshair to charged type
            crosshair_charged.set_alpha(255)


        if event.type == BDE_AFTER_SOUND:
            bullet_charged = True

        if event.type == KEYDOWN:
            if event.key == K_f:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    last_size = current_size
                    current_size = FULLSCREEN_SIZE
                    screen = display.set_mode(current_size, FULLSCREEN)
                else:
                    current_size = last_size
                    screen = display.set_mode(current_size, RESIZABLE)

        # hovering a status screen
        button_x = 600
        button_y = 400
        x_len = status_screen.get_width()
        y_len = status_screen.get_height()
        mos_x, mos_y = pygame.mouse.get_pos()
        if mos_x > button_x and (mos_x < button_x + x_len):
            x_inside = True
        else:
            x_inside = False
        if mos_y > button_y and (mos_y < button_y + y_len):
            y_inside = True
        else:
            y_inside = False
        if x_inside and y_inside:
            screen.blit(status_screen, (button_x, button_y))
            status_screen_hovering = True
        else:
            status_screen_hovering = False

        #out of ammo indication
        if remaining_bullets == 0 and not status_screen_hovering:
            uncharged_text.set_alpha(255)
            charged_text.set_alpha(0)
        #clip recharging
        if remaining_bullets != bullets_per_clip and status_screen_hovering:
            uncharged_text.set_alpha(0)
            charged_text.set_alpha(0)
            if not recharging_procces:
                recharging_procces = True
            pygame.time.set_timer(RECHARGING_EVENT, recharging_delay, True)

        if event.type == RECHARGING_EVENT and recharging_procces and status_screen_hovering:
            remaining_bullets += 1
            recharge_text.set_alpha(255)
            charged_text.set_alpha(0)
            uncharged_text.set_alpha(0)
            if remaining_bullets != bullets_per_clip:
                pygame.time.set_timer(RECHARGING_EVENT, recharging_delay, True)
                recharging_sound = random.choice(recharging_sounds)
                recharging_sound.play()
            else:
                bullet_charged_sound.play()
                pygame.time.set_timer(BDE_AFTER_SOUND, bcd_after_sound, True)
                recharging_procces = False
                crosshair_charged.set_alpha(255)
                charged_text.set_alpha(255)
                recharge_text.set_alpha(0)

        if not status_screen_hovering and recharging_procces and remaining_bullets != 0:
                bullet_charged_sound.play()
                pygame.time.set_timer(BDE_AFTER_SOUND, bcd_after_sound, True)
                recharging_procces = False
                crosshair_charged.set_alpha(255)
                recharge_text.set_alpha(0)
                charged_text.set_alpha(255)

#############SPAWNING#ENEMIES#######################
    spawnrate = max_spawnrate - (0.3 * current_enemies_count)

    if random.randrange(0, 1000) < spawnrate and enemy_max_count != current_enemies_count:
        current_enemies_count += 1
        sanity_decreasing += 1
        enemy = Shadow(10)
        shadow_group.add(enemy)
        all_sprites.add(enemy)

        for enemy in shadow_group:
            enemy.draw()


    #sanity decreasing
    if sanity_bar.sanity > 0:
        sanity_bar.sanity -= sanity_decreasing_total
    if sanity_bar.sanity < 50 and sanity_bar.sanity > 0:
        ls_opacity += sanity_decreasing_total * 5
        if sanity_bar.sanity >= 45:
            insanity_ambient_sound.set_volume(0.05 / (sanity_bar.sanity / 100))
        else:
            insanity_ambient_sound.set_volume(0.1 / (sanity_bar.sanity / 100))

    insanity_whispering_sound.set_volume(sanity_decreasing_total * 2)
    low_sanity_indication.set_alpha(ls_opacity)

    if sanity_bar.sanity <= 0:
        max_spawnrate = 6666
        enemy_max_count = 666
        if current_enemies_count == 666:
            running = False



################DRAWING#SPRITES#AND#OBJECTS############################
    # draw the background
    for bg_x in range(0, game_width, images['bg'].get_width()):
        for bg_y in range(0, game_height, images['bg'].get_height()):
            game_window.blit(images['bg'], (bg_x, bg_y))

#####draw enemies
    shadow_group.update()
    for enemy in shadow_group:
        enemy.draw()

    # draw the table
    for table_x in range(0, game_width, images['table'].get_width()):
        game_window.blit(images['table'], (table_x, game_height - 80))

    # draw remaining bullets
    for i in range(remaining_bullets):
        game_window.blit(images['bullet'], (i * 20 + 15, game_height - 70))

    # draw statuses
    status_x = game_width - images['status'].get_width()
    status_y = 400
    game_window.blit(status_screen, (status_x, status_y))

    charged_x = status_x + (images['status'].get_width() / 5)
    charged_y = status_y + (images['status'].get_height() / 3)
    game_window.blit(charged_text, (charged_x, charged_y))

    uncharged_x = status_x + (images['status'].get_width() / 5)
    uncharged_y = status_y + (images['status'].get_height() / 3)
    game_window.blit(uncharged_text, (uncharged_x, uncharged_y))

    recharge_x = status_x + (images['status'].get_width() / 5)
    recharge_y = status_y + (images['status'].get_height() / 3)
    game_window.blit(recharge_text, (recharge_x, recharge_y))

    # draw sanity bar
    sanity_bar.draw(screen)

    # draw the crosshair
    crosshair_x, crosshair_y = pygame.mouse.get_pos()
    crosshair_x -= images['crosshair'].get_width() / 2
    crosshair_y -= images['crosshair'].get_height() / 2
    game_window.blit(images['crosshair'], (crosshair_x, crosshair_y))

    #draw charged crosshair
    game_window.blit(crosshair_charged, (crosshair_x, crosshair_y))

    #draw score
    display_score()

    # draw low sanity effect
    game_window.blit(low_sanity_indication, (0, 0))


    pygame.display.update()


# while recharge:
       # clock.tick(fps)

    #    pygame.display.update()

        #for event in pygame.event.get():
         #   if event.type == QUIT:
         #       recharge = False
         #       running = False
        #    if event.type == MOUSEBUTTONDOWN:
       #         recharge = False
        #        running = True
         #       new_game()

pygame.quit()