import random
import numpy as np


class Snake:
    SCREEN_WIDTH = 400
    SCREEN_HEIGHT = 300
    SNAKE_BLOCK = 10

    def __init__(self):
        self.food_position = None
        self.game_over = False
        self.is_eating = False
        self.snake_positions = []
        self.snake_length = 1
        self.position = np.array([
            self.SCREEN_WIDTH / 2,
            self.SCREEN_HEIGHT / 2
        ])
        self.displacement = np.zeros(2, )
        self.create_food()

    def update_snake_head_position(self):
        self.position += self.displacement

    def check_collisions(self):
        if (self.position[0] >= self.SCREEN_WIDTH
                or self.position[0] < 0
                or self.position[1] >= self.SCREEN_HEIGHT
                or self.position[1] < 0):
            self.game_over = True
            print("Game over: Screen border")
        for segment in self.snake_positions[:-1]:
            if np.array_equal(segment, self.position):
                self.game_over = True
                print("Game over: Own body crash")

    def update_snake_body(self):
        self.snake_positions.append([self.position[0], self.position[1]])
        if len(self.snake_positions) > self.snake_length:
            del self.snake_positions[0]

    def create_food(self):
        self.food_position = np.array((
            round(random.randrange(0, self.SCREEN_WIDTH - self.SNAKE_BLOCK) / 10.0) * 10.0,
            round(random.randrange(0, self.SCREEN_HEIGHT - self.SNAKE_BLOCK) / 10.0) * 10.0
        ))

    def eat_food(self):
        self.is_eating = np.array_equal(self.position, self.food_position)
        if self.is_eating:
            self.snake_length += 1
            self.create_food()

    def process(self):
        self.update_snake_head_position()
        self.check_collisions()
        self.update_snake_body()
        self.eat_food()
