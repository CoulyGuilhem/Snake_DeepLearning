import random

import numpy as np

import snake
from model import QLearning


class SnakeAgent(snake.Snake):
    STRAIGHT = 0
    RIGHT = 1
    LEFT = 2

    def __init__(self):
        super().__init__()
        self.last_action = None
        self.cumul_reward = None
        self.food_distance = None
        self.q_learning = QLearning()
        self.q_table = {}
        self.reset()

    def reset(self):
        super().__init__()

        self.food_distance = self.compute_food_distance()
        self.cumul_reward = 0
        self.last_action = "epsilon"

        self.displacement = np.array([0, -self.SNAKE_BLOCK])

    def compute_food_distance(self):
        return np.linalg.norm(self.food_position - self.position)

    def get_state(self, display=False):
        FOOD_FRONT = 1 << 0  # !< 0b0001
        FOOD_BACK = 1 << 1  # !< 0b0010
        FOOD_RIGHT = 1 << 2  # !< 0b0100
        FOOD_LEFT = 1 << 3  # !< 0b1000

        DANGER_STRAIGHT = 1 << 0  # !< 0b001
        DANGER_RIGHT = 1 << 1  # !< 0b010
        DANGER_LEFT = 1 << 2  # !< 0b100

        # Calculate normalized direction vectors
        direction = self.displacement / np.linalg.norm(self.displacement)
        food_vector = self.food_position - self.position
        food_distance = np.linalg.norm(food_vector)

        food_direction = food_vector / food_distance if food_distance != 0 else np.array([0, 0])

        # Calculate relative food position using dot and cross products
        forward_component = np.dot(direction, food_direction)
        right_component = np.cross(direction, food_direction)

        food_bits = 0
        if forward_component > 0:
            food_bits |= FOOD_FRONT
        else:
            food_bits |= FOOD_BACK
        if right_component > 0:
            food_bits |= FOOD_RIGHT
        else:
            food_bits |= FOOD_LEFT

        danger_bits = 0
        if self._is_danger(self.displacement):
            danger_bits |= DANGER_STRAIGHT
        if self._is_danger(self._turn_right()):
            danger_bits |= DANGER_RIGHT
        if self._is_danger(self._turn_left()):
            danger_bits |= DANGER_LEFT

        if display:
            self._display_state_info(food_bits, danger_bits)

        return (food_bits, danger_bits)

    def _turn_right(self):
        return np.array([-self.displacement[1], self.displacement[0]])

    def _turn_left(self):
        return np.array([self.displacement[1], -self.displacement[0]])

    def _apply_action(self, action):
        if int(action) == self.RIGHT:
            self.displacement = self._turn_right()
        elif int(action) == self.LEFT:
            self.displacement = self._turn_left()

    def _is_danger(self, direction):
        test_pos = self.position + direction
        if (test_pos[0] < 0 or test_pos[0] >= self.SCREEN_WIDTH
                or test_pos[1] < 0 or test_pos[1] >= self.SCREEN_HEIGHT):
            return True

        return any(np.array_equal(test_pos, segment) for segment in self.snake_positions[:-1])

    def choose_action(self, state):
        if random.random() < self.q_learning.exploration_rate:
            self.last_action = "epsilon"
            return random.choice([self.STRAIGHT, self.RIGHT, self.LEFT])

        self.last_action = "q_table"
        state_key = str(state)

        if state_key not in self.q_table:
            self.q_table[state_key] = {
                self.STRAIGHT: 0,
                self.RIGHT: 0,
                self.LEFT: 0
            }
        return max(self.q_table[state_key], key=self.q_table[state_key].get)

    def calculate_reward(self):
        if self.game_over:
            return self.q_learning.death_penalty
        if self.is_eating:
            return self.q_learning.food_reward
        return self.q_learning.distance_reward * (self.food_distance - self.compute_food_distance())


