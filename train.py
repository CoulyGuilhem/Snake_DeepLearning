import argparse
import json

import pygame
import matplotlib.pyplot as plt
import numpy as np

import agent
from snake_interface import SnakeInterface


class Train:
    def __init__(self, q_table_file=None, tick=15):
        super().__init__()
        self.scores = []
        self.interface = SnakeInterface()
        self.agent = agent.SnakeAgent()
        self.q_table_file = q_table_file
        self.speed = tick

    def _load_q_table(self):
        if self.q_table_file:
            try:
                with open(self.q_table_file, 'r') as f:
                    data = json.load(f)
                    self.agent.q_table = data
                    self.agent.q_learning.exploration_rate = 0
                    print(f"Q-table chargée depuis {self.q_table_file} avec exploration_rate={self.agent.q_learning.exploration_rate}")
            except FileNotFoundError:
                print(f"Fichier {self.q_table_file} non trouvé, démarrage avec une table vide")
                self.agent.q_table = {}

    def _plot_training_progress(self, save_path="training_snake.png"):
        if len(self.scores) > 1:
            plt.figure(figsize=(10, 6))
            plt.plot(self.scores, label='Scores', alpha=0.3, color='blue')
            window_size = max(10, len(self.scores) // 20)
            moving_avg = np.convolve(self.scores, np.ones(window_size) / window_size, mode='valid')
            plt.plot(range(window_size - 1, len(self.scores)), moving_avg,
                     label=f'Moving Average ({window_size} épisodes)', color='red', linewidth=2)
            plt.xlabel('Épisodes')
            plt.ylabel('Score')
            plt.title('Progression de l\'entraînement')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(save_path, dpi=300)
            plt.show()

    def train(self, num_episodes=100):
        pygame.init()
        pygame.display.set_caption('Training')

        for episode in range(num_episodes):
            self.agent.reset()
            self.interface.snake = self.agent
            self.interface.close_window = False

            while not self.agent.game_over and not self.interface.close_window:
                self.interface.handle_events()
                current_state = self.agent.get_state()
                action = self.agent.choose_action(current_state)

                self.agent._apply_action(action)
                self.agent.process()

                new_state = self.agent.get_state()
                reward = self._calculate_reward()
                self.agent.cumul_reward += reward

                self._update_q_table(current_state, action, reward, new_state)

                self.interface.display.fill((20, 20, 20))
                pygame.draw.rect(self.interface.display, (255, 40, 40), [
                    self.agent.food_position[0], self.agent.food_position[1],
                    self.agent.SNAKE_BLOCK, self.agent.SNAKE_BLOCK
                ])
                self.interface.draw_snake()
                self.interface.display_score()
                pygame.display.update()

                self.interface.clock.tick(self.speed)

            score = self.agent.snake_length - 1
            self.scores.append(score)

            print(f"Épisode {episode} terminé : Score = {score}, Dernière récompense = {self.agent.cumul_reward}, "
                  f"Taux d'exploration = {self.agent.q_learning.exploration_rate}, Dernière action : {self.agent.last_action}")

            if episode % 10 == 0:
                avg_score = sum(self.scores[-10:]) / min(10, len(self.scores))
                print(f"Score moyen (10 derniers) = {avg_score:.1f}")

            self.agent.q_learning.exploration_rate *= self.agent.q_learning.exploration_decay

        self._plot_training_progress()
        return self.agent.q_table, self.scores

    def play(self, qtable, num_games=1):
        pygame.init()
        pygame.display.set_caption('Play Mode')

        for game in range(num_games):
            self.agent.reset()
            self.q_table_file = qtable
            self._load_q_table()
            self.interface.snake = self.agent
            self.interface.close_window = False

            self.agent.q_learning.exploration_rate = 0

            while not self.agent.game_over and not self.interface.close_window:
                self.interface.handle_events()
                current_state = self.agent.get_state()
                action = self.agent.choose_action(current_state)  # Utilisation de la meilleure action
                self.agent._apply_action(action)
                self.agent.process()

                self.interface.display.fill((20, 20, 20))
                pygame.draw.rect(self.interface.display, (255, 40, 40), [
                    self.agent.food_position[0], self.agent.food_position[1],
                    self.agent.SNAKE_BLOCK, self.agent.SNAKE_BLOCK
                ])
                self.interface.draw_snake()
                self.interface.display_score()
                pygame.display.update()

                self.interface.clock.tick(self.speed)

            score = self.agent.snake_length - 1
            print(f"Partie {game + 1} terminée : Score = {score}")

    def _calculate_reward(self):
        food_distance = self.agent.compute_food_distance()
        if self.agent.game_over:
            return self.agent.q_learning.death_penalty

        if self.agent.is_eating:
            return self.agent.q_learning.food_reward

        distance_delta = self.agent.food_distance - food_distance
        reward = distance_delta * self.agent.q_learning.distance_reward

        self.agent.food_distance = food_distance
        return reward

    def _update_q_table(self, state, action, reward, next_state):
        state_key = str(state)
        next_state_key = str(next_state)

        if state_key not in self.agent.q_table:
            self.agent.q_table[state_key] = {self.agent.STRAIGHT: 0, self.agent.RIGHT: 0, self.agent.LEFT: 0}

        if next_state_key not in self.agent.q_table:
            self.agent.q_table[next_state_key] = {self.agent.STRAIGHT: 0, self.agent.RIGHT: 0, self.agent.LEFT: 0}

        current_q = self.agent.q_table[state_key][action]
        max_next_q = max(self.agent.q_table[next_state_key].values())
        new_q = current_q + self.agent.q_learning.learning_rate * (
                reward + self.agent.q_learning.discount_factor * max_next_q - current_q)

        self.agent.q_table[state_key][action] = new_q


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Snake RL Training',
        description='Q-Learning algorithm to train or play Snake')
    parser.add_argument('--mode', type=str, choices=['train', 'play'], required=True, help='Mode: train (entraînement) ou play (jouer)')
    parser.add_argument('--episodes', type=int, default=1000, help="Nombre d'épisodes pour l'entraînement")
    parser.add_argument('--games', type=int, default=1, help="Nombre de parties en mode jeu")
    parser.add_argument('--qtable', type=str, default='snake_q_table.json', help='Fichier de sauvegarde de la Q-table')
    parser.add_argument('--tick', type=int, default=15, help='Vitesse du jeu')

    args = parser.parse_args()

    trainer = Train(q_table_file=args.qtable, tick=args.tick)

    if args.mode == 'train':
        q_table, scores = trainer.train(num_episodes=args.episodes)
        with open(args.qtable, 'w') as f:
            json.dump({k: {str(k2): v2 for k2, v2 in v.items()} for k, v in q_table.items()}, f)
        print(f"Q-table sauvegardée dans {args.qtable}")
    elif args.mode == 'play':
        trainer.play(num_games=args.games, qtable=args.qtable)
