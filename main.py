import json
import os
import random
import time

import pygame

pygame.init()
pygame.joystick.init()
random.seed(int(time.time()))

try:
    joystick = pygame.joystick.Joystick(0)
except pygame.error:
    joystick = None

SCREEN_HEIGHT = 1080
SCREEN_WIDTH = 1920
SCREEN = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    pygame.NOFRAME,
    vsync=True)
CENTER_RECT = (SCREEN.get_width() // 2, SCREEN.get_height() // 2)
CENTER_RECT_1_8 = (SCREEN.get_width() // 2, SCREEN.get_height() // 8)
best_record = 0


def load_image(file_name, width=None, height=None):
    image = pygame.image.load(
        os.path.join("Assets", "images", file_name))
    if not width and not height:
        return pygame.transform.scale(image, (
            image.get_width() // 2, image.get_height() // 2))
    elif height and not width:
        return pygame.transform.scale(image,
                                      (
                                          image.get_width() * height // image.get_height(),
                                          height))
    return pygame.transform.scale(image, (width, height))


RUNNING = [
    load_image("klenin_1.png"),
    load_image("klenin_2.png"),
]

STUDENTS = [
    load_image("student_1.png"),
    load_image("student_2.png"),
    load_image("student_3.png"),
    load_image("student_4.png"),
    load_image("student_5.png"),
    load_image("student_6.png"),
    load_image("student_7.png"),
    load_image("student_8.png"),
    load_image("student_9.png"),
    load_image("student_10.png"),
]

COFFEE = load_image("coffee.png")

BACKGROUND = load_image("background.png",
                        height=SCREEN.get_height())

BACKGROUND_START = load_image("background_start.png",
                              height=SCREEN.get_height())
BACKGROUND_START.get_rect().center = CENTER_RECT

BACKGROUND_NEW_RECORD = load_image("background_new_record.png",
                                   height=SCREEN.get_height())
BACKGROUND_NEW_RECORD.get_rect().center = CENTER_RECT

FONT = "Assets/Fifaks10Dev1.ttf"

BACKGROUND_SOUND = pygame.mixer.Sound("Assets/background.mp3")
DEATHSCREAN_SOUND = pygame.mixer.Sound("Assets/deathscream.wav")
COIN_SOUND = pygame.mixer.Sound("Assets/coin.wav")

with open('Assets/text.json') as f:
    TEXT = json.load(f)


def get_random_item_from_list(items):
    return items[random.randint(0, len(items) - 1)]


class Klenin:

    def __init__(self):
        self.run_img = RUNNING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.BOUND_Y_POS = SCREEN.get_height() - self.run_img[
            0].get_height() - 10
        self.BOUND_X_POS = 40
        self.JUMP_VEL = 14

        self.step_index = 0
        self.image_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.y = self.BOUND_Y_POS
        self.dino_rect.x = self.BOUND_X_POS

    def update(self, user_input, joystick):
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0
            self.image_index += 1
            self.image_index %= len(self.run_img)

        if (user_input[pygame.K_UP] or (
                joystick and joystick.get_button(0))) and not self.dino_jump:
            self.dino_run = False
            self.dino_jump = True
        elif not (self.dino_jump or user_input[pygame.K_DOWN]):
            self.dino_run = True
            self.dino_jump = False

    def run(self):
        self.image = self.run_img[self.image_index]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.BOUND_X_POS
        self.dino_rect.y = self.BOUND_Y_POS
        self.step_index += 1

    def jump(self):
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 3
            self.jump_vel -= 0.4
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Obstacle:
    def __init__(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN.get_height() - self.image.get_height() - 10
        self.deleted = False

    def update(self):
        self.rect.move_ip(-game_speed, 0)
        if self.rect.x < -self.rect.width:
            self.deleted = True

    def draw(self, SCREEN):
        SCREEN.blit(self.image, self.rect)

    def get_range_from_left_side_of_screen(self):
        return SCREEN_WIDTH - self.rect.x

    def is_deleted(self):
        return self.deleted


def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, best_record
    run = True
    clock = pygame.time.Clock()
    player = Klenin()
    score = 0
    game_speed = 15
    x_pos_bg = 0
    y_pos_bg = 0
    points = 0
    font_30 = pygame.font.Font(FONT, 30)
    obstacles = []
    coffees = []
    death_count = 0
    time_of_start_game = time.time()

    BACKGROUND_SOUND.play()

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BACKGROUND.get_width()
        SCREEN.blit(BACKGROUND, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BACKGROUND, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BACKGROUND, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed * 0.6

    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        user_input = pygame.key.get_pressed()

        if len(obstacles) == 0 and time.time() - time_of_start_game > 3:
            obstacles.append(
                Obstacle(STUDENTS[random.randint(0, len(STUDENTS) - 1)]))

        SCREEN.fill((0, 0, 0))
        background()

        score_text = font_30.render(f"Score: {score}", True, (0, 0, 0))
        score_text_rect = score_text.get_rect()
        score_text_rect.topright = (SCREEN.get_width() - 20, 20)

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if obstacle.is_deleted():
                obstacles.remove(obstacle)
            value = random.randint(400, SCREEN.get_width() * 3 // 2)
            if len(coffees) == 0 and obstacle.get_range_from_left_side_of_screen() >= value:
                coffees.append(Obstacle(COFFEE))
            if player.dino_rect.colliderect(obstacle.rect):
                BACKGROUND_SOUND.stop()
                DEATHSCREAN_SOUND.play()
                best_record = max(best_record, score)
                pygame.time.delay(2000)
                death_count += 1
                menu(death_count)

        for coffee in coffees:
            coffee.draw(SCREEN)
            coffee.update()
            if player.dino_rect.colliderect(coffee.rect):
                COIN_SOUND.stop()
                COIN_SOUND.play()
                score += 1
                coffees.remove(coffee)
                game_speed += 1
            if coffee.is_deleted():
                coffees.remove(coffee)

        player.draw(SCREEN)
        player.update(user_input, joystick)
        SCREEN.blit(score_text, score_text_rect)
        pygame.display.update()


def menu(death_count):
    global points, text
    run = True
    start_text = get_random_item_from_list(TEXT['start'])
    gameover_text = get_random_item_from_list(TEXT['gameover'])

    while run:
        SCREEN.fill((255, 255, 255))
        SCREEN.blit(BACKGROUND_START, BACKGROUND_START.get_rect())
        font = pygame.font.Font(FONT, 30)

        best_record_text = font.render(f"Best record: {best_record}",
                                       True, (0, 0, 0)
                                       )
        best_record_text_rect = best_record_text.get_rect()
        best_record_text_rect.center = CENTER_RECT_1_8

        if death_count == 0:
            text = font.render(start_text, True, (0, 0, 0))
        elif death_count > 0:
            text = font.render(gameover_text, True, (0, 0, 0))

        text_rect = text.get_rect()
        text_rect.center = CENTER_RECT
        SCREEN.blit(text, text_rect)
        SCREEN.blit(best_record_text, best_record_text_rect)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN or (
                    joystick and joystick.get_button(
                pygame.CONTROLLER_BUTTON_A)):
                main()


menu(death_count=0)
