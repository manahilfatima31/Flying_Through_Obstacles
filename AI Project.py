from __future__ import print_function
import pygame
import time
import os
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 550
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

FONT = pygame.font.SysFont('Arial', 20)
FONT_COLOR = (255, 255, 255) #white font

BIRD_IMGS = [pygame.image.load('plane1.png'),
             pygame.image.load('plane1.png'),
             pygame.image.load('plane1.png')]
BOTTOM_PIPE_IMG = pygame.image.load('obstacle.png')
TOP_PIPE_IMG = pygame.transform.flip(BOTTOM_PIPE_IMG, False, True)
FLOOR_IMG = pygame.image.load('floor.png')
BG_IMG = pygame.transform.scale(pygame.image.load('bg.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))


FPS = 30
max_score = 5000

#floor options
floor_velocity = 5
floor_starting_y_position = 500

#pipe options
pipe_max_num = 5000
pipe_vertical_gap = 100
pipe_horizontal_gap = 200
pipe_velocity = 5
top_pipe_min_height = 85

top_pipe_max_height = 320
pipe_starting_x_position = 500

#bird options
bird_max_upward_angle = 35
bird_max_downward_angle = -90
bird_min_incremental_angle = 5
bird_angular_acceleration = 0.3
bird_jump_velocity = -8
bird_acceleration = 3
bird_max_displacement = 11
bird_starting_x_position = 150
bird_starting_y_position = 250


class Bird:
    IMGS = BIRD_IMGS
    MAX_UPWARD_ANGLE = bird_max_upward_angle
    MAX_DOWNWARD_ANGLE = bird_max_downward_angle

    def __init__(self, x_position, y_position):
        self.bird_img = self.IMGS[0]
        self.x = x_position
        self.y = y_position
        self.fly_angle = 0
        self.time = 0
        self.velocity = 0
        self.index = 0

    def move(self):
        self.time += 1



        displacement = self.velocity * self.time + (
                    1 / 2) * bird_acceleration * self.time ** 2


        if displacement > bird_max_displacement:
            displacement = bird_max_displacement

        self.y = self.y + displacement

        if displacement < 0:
            if self.fly_angle < self.MAX_UPWARD_ANGLE:
                self.fly_angle += max(bird_angular_acceleration * (self.MAX_UPWARD_ANGLE - self.fly_angle),
                                      bird_min_incremental_angle)
            elif self.fly_angle >= self.MAX_UPWARD_ANGLE:
                self.fly_angle = self.MAX_UPWARD_ANGLE

        else:
            if self.fly_angle > self.MAX_DOWNWARD_ANGLE:
                self.fly_angle -= abs(min(bird_angular_acceleration * (self.MAX_DOWNWARD_ANGLE - self.fly_angle),
                                          -bird_min_incremental_angle))
            elif self.fly_angle <= self.MAX_DOWNWARD_ANGLE:
                self.fly_angle = self.MAX_DOWNWARD_ANGLE

    def jump(self):
        self.velocity = bird_jump_velocity
        self.time = 0

    def update(self):

        if self.fly_angle < -45:
            self.bird_img = self.IMGS[0]
            self.index = 0


        elif self.index >= len(self.IMGS):
            self.index = 0

        self.bird_img = self.IMGS[self.index]
        self.index += 1

        rotated_image = pygame.transform.rotate(self.bird_img, self.fly_angle)

        origin_img_center = self.bird_img.get_rect(topleft=(self.x, self.y)).center

        rotated_rect = rotated_image.get_rect(center=origin_img_center)

        return rotated_image, rotated_rect


class Pipe:
    VERTICAL_GAP = pipe_vertical_gap
    VELOCITY = pipe_velocity
    IMG_WIDTH = TOP_PIPE_IMG.get_width()
    IMG_LENGTH = TOP_PIPE_IMG.get_height()

    def __init__(self, x_position):
        self.top_pipe_img = TOP_PIPE_IMG
        self.bottom_pipe_img = BOTTOM_PIPE_IMG
        self.x = x_position
        self.top_pipe_height = 0
        self.top_pipe_topleft = 0
        self.bottom_pipe_topleft = 0
        self.random_height()

    def move(self):
        self.x -= self.VELOCITY

    def random_height(self):
        self.top_pipe_height = random.randrange(top_pipe_min_height,
                                                top_pipe_max_height)
        self.top_pipe_topleft = self.top_pipe_height - self.IMG_LENGTH
        self.bottom_pipe_topleft = self.top_pipe_height + self.VERTICAL_GAP


class Floor:
    IMGS = [FLOOR_IMG, FLOOR_IMG, FLOOR_IMG]
    VELOCITY = floor_velocity
    IMG_WIDTH = FLOOR_IMG.get_width()

    def __init__(self, y_position):
        self.x1 = 0
        self.x2 = self.IMG_WIDTH
        self.x3 = self.IMG_WIDTH * 2
        self.y = y_position

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY
        self.x3 -= self.VELOCITY

        if self.x1 + self.IMG_WIDTH < 0:
            self.x1 = self.x3 + self.IMG_WIDTH
        if self.x2 + self.IMG_WIDTH < 0:
            self.x2 = self.x1 + self.IMG_WIDTH
        if self.x3 + self.IMG_WIDTH < 0:
            self.x3 = self.x2 + self.IMG_WIDTH


def collide(bird, pipe, floor, screen):
    bird_mask = pygame.mask.from_surface(bird.bird_img)
    top_pipe_mask = pygame.mask.from_surface(pipe.top_pipe_img)
    bottom_pipe_mask = pygame.mask.from_surface(pipe.bottom_pipe_img)

    sky_height = 0
    floor_height = floor.y
    bird_lower_end = bird.y + bird.bird_img.get_height()

    top_pipe_offset = (round(pipe.x - bird.x), round(pipe.top_pipe_topleft - bird.y))
    bottom_pipe_offset = (round(pipe.x - bird.x), round(pipe.bottom_pipe_topleft - bird.y))

    top_pipe_intersection_point = bird_mask.overlap(top_pipe_mask, top_pipe_offset)
    bottom_pipe_intersection_point = bird_mask.overlap(bottom_pipe_mask, bottom_pipe_offset)

    if top_pipe_intersection_point is not None or bottom_pipe_intersection_point is not None or bird_lower_end > floor_height or bird.y < sky_height:
        return True
    else:
        return False


def draw_game(screen, birds, pipes, floor, score, generation, game_time):
    screen.blit(BG_IMG, (0, 0))

    screen.blit(floor.IMGS[0], (floor.x1, floor.y))
    screen.blit(floor.IMGS[1], (floor.x2, floor.y))
    screen.blit(floor.IMGS[2], (floor.x3, floor.y))

    for pipe in pipes:
        screen.blit(pipe.top_pipe_img, (pipe.x, pipe.top_pipe_topleft))
        screen.blit(pipe.bottom_pipe_img, (pipe.x, pipe.bottom_pipe_topleft))

    for bird in birds:
        rotated_image, rotated_rect = bird.update()
        screen.blit(rotated_image, rotated_rect)

    score_text = FONT.render('Score: ' + str(score), 1, FONT_COLOR)
    screen.blit(score_text, (SCREEN_WIDTH - 15 - score_text.get_width(), 15))

    game_time_text = FONT.render('Timer: ' + str(game_time) + ' s', 1,
                                 FONT_COLOR)
    screen.blit(game_time_text,
                (SCREEN_WIDTH - 15 - game_time_text.get_width(), 15 + score_text.get_height()))

    generation_text = FONT.render('Generation: ' + str(generation - 1), 1,
                                  FONT_COLOR)
    screen.blit(generation_text, (15, 15))

    bird_text = FONT.render('Birds Alive: ' + str(len(birds)), 1,
                            FONT_COLOR)
    screen.blit(bird_text, (15, 15 + generation_text.get_height()))

    progress_text = FONT.render('Pipes Remained: ' + str(len(pipes) - score), 1,
                                FONT_COLOR)
    screen.blit(progress_text, (15, 15 + generation_text.get_height() + bird_text.get_height()))

    pygame.display.update()


generation = 0
max_gen = 50
prob_threshold_to_jump = 0.8
failed_punishment = 10


def get_index(pipes, birds):
    bird_x = birds[0].x
    list_distance = [pipe.x + pipe.IMG_WIDTH - bird_x for pipe in pipes]
    index = list_distance.index(min(i for i in list_distance if i >= 0))
    return index


import neat


def main(genomes, config):
    global generation, SCREEN
    screen = SCREEN
    generation += 1

    score = 0
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()

    floor = Floor(floor_starting_y_position)
    pipes_list = [Pipe(pipe_starting_x_position + i * pipe_horizontal_gap) for i in
                  range(pipe_max_num)]

    models_list = []
    genomes_list = []
    birds_list = []

    for genome_id, genome in genomes:
        birds_list.append(
            Bird(bird_starting_x_position, bird_starting_y_position))
        genome.fitness = 0
        genomes_list.append(genome)
        model = neat.nn.FeedForwardNetwork.create(genome, config)
        models_list.append(model)

    run = True

    while run is True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

            #keys = pygame.key.get_pressed()
            #if keys[pygame.K_w]:
                #bird.jump()


        if score >= max_score or len(birds_list) == 0:
            run = False
            break

        game_time = round((pygame.time.get_ticks() - start_time) / 1000, 2)

        clock.tick(
            FPS)

        floor.move()

        pipe_input_index = get_index(pipes_list, birds_list)

        passed_pipes = []
        for pipe in pipes_list:
            pipe.move()
            if pipe.x + pipe.IMG_WIDTH < birds_list[0].x:
                passed_pipes.append(pipe)

        score = len(
            passed_pipes)

        for index, bird in enumerate(birds_list):
            bird.move()
            delta_x = bird.x - pipes_list[
                pipe_input_index].x
            delta_y_top = bird.y - pipes_list[
                pipe_input_index].top_pipe_height
            delta_y_bottom = bird.y - pipes_list[
                pipe_input_index].bottom_pipe_topleft
            net_input = (delta_x, delta_y_top, delta_y_bottom)
            output = models_list[index].activate(net_input)

            if output[0] > prob_threshold_to_jump:
                bird.jump()

            bird_failed = True if collide(bird, pipes_list[pipe_input_index], floor, screen) is True else False

            genomes_list[index].fitness = game_time + score - bird_failed * failed_punishment

            if bird_failed:
                models_list.pop(index)
                genomes_list.pop(index)
                birds_list.pop(index)

        draw_game(screen, birds_list, pipes_list, floor, score, generation, game_time)


def run_NEAT(config_file):

    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_file)

    neat_pop = neat.population.Population(config)

    neat_pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    neat_pop.add_reporter(stats)

    neat_pop.run(main, max_gen)

    winner = stats.best_genome()

    node_names = {-1: 'delta_x', -2: 'delta_y_top', -3: 'delta_y_bottom', 0: 'Jump or Not'}
    draw_net(config, winner, True, node_names=node_names)
    plot_stats(stats, ylog=False, view=True)
    plot_species(stats, view=True)

    print('\nBest genome:\n{!s}'.format(winner))


# main
config_file = 'config-feedforward.txt'
run_NEAT(config_file)


