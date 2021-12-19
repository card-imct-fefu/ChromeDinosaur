import os
import json
import random

import pygame

pygame.init()
pygame.joystick.init()

try:
    joystick = pygame.joystick.Joystick(0)
except pygame.error:
    joystick = None

SCREEN_HEIGHT = 1080
SCREEN_WIDTH = 1920
SCREEN = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    pygame.FULLSCREEN,
    vsync=True)


def load_image(file_name, width=None, height=None):
    image = pygame.image.load(os.path.join("Assets", file_name))
    if not width and not height:
        return pygame.transform.scale(image, (image.get_width() // 2, image.get_height() // 2))
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
]

BACKGROUND = load_image("background.png", SCREEN.get_width(), SCREEN.get_height())

FONT = "Assets/Fifaks10Dev1.ttf"

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

        self.BOUND_Y_POS = SCREEN.get_height() - self.run_img[0].get_height()
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

        if (user_input[pygame.K_UP] or (joystick and joystick.get_button(0))) and not self.dino_jump:
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


class Student:
    def __init__(self, image, number):
        self.image = image[number]
        self.number = number
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN.get_height() - self.image.get_height()

    def update(self):
        self.rect.move_ip(-game_speed, 0)
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image, self.rect)


def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Klenin()
    game_speed = 13
    x_pos_bg = 0
    y_pos_bg = 0
    points = 0
    font = pygame.font.Font(FONT, 20)
    obstacles = []
    death_count = 0

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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # SCREEN.fill((255, 255, 255))
        user_input = pygame.key.get_pressed()

        if len(obstacles) == 0:
            obstacles.append(Student(STUDENTS, random.randint(0, len(STUDENTS) - 1)))

        SCREEN.fill((0, 0, 0))
        background()
        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                pygame.time.delay(2000)
                death_count += 1
                menu(death_count)

        player.draw(SCREEN)
        player.update(user_input, joystick)
        clock.tick(60)
        pygame.display.update()


def menu(death_count):
    global points, text
    run = True
    start_text = get_random_item_from_list(TEXT['start'])
    gameover_text = get_random_item_from_list(TEXT['gameover'])

    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font(FONT, 30)

        if death_count == 0:
            text = font.render(start_text, True, (0, 0, 0))
        elif death_count > 0:
            text = font.render(gameover_text, True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (SCREEN.get_width() // 2, SCREEN.get_height() // 2)
        SCREEN.blit(text, text_rect)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN or (joystick and joystick.get_button(pygame.CONTROLLER_BUTTON_A)):
                main()


menu(death_count=0)
