import random


class QLearning:
    def __init__(self,
                 learning_rate=0.001,
                 discount_factor=0.99,
                 exploration_rate=1.0,
                 exploration_decay=0.997,
                 food_reward=150,
                 death_penalty=-250,
                 distance_reward=2):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.food_reward = food_reward
        self.death_penalty = death_penalty
        self.distance_reward = distance_reward
        self.q_table = {}

    def choose_action(self, state):
        if random.random() < self.exploration_rate:
            return random.choice([0, 1, 2])
        return max(self.q_table.get(state, {0: 0, 1: 0, 2: 0}), key=self.q_table[state].get)

    def update_q_table(self, state, action, reward, next_state):
        state_key = str(state)
        next_state_key = str(next_state)
        if state_key not in self.q_table:
            self.q_table[state_key] = {0: 0, 1: 0, 2: 0}
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = {0: 0, 1: 0, 2: 0}
        max_next_q = max(self.q_table[next_state_key].values())
        self.q_table[state_key][action] += self.learning_rate * (
                    reward + self.discount_factor * max_next_q - self.q_table[state_key][action])
