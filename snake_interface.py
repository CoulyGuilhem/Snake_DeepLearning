import pygame
from collections import deque
import snake

pygame.init()
pygame.display.set_caption('Snake')

HEAD = (100, 255, 100)
BODY = (0, 155, 0)
FRUIT = (255, 40, 40)
BACKGROUND = (20, 20, 20)
FONT_STYLE = pygame.font.SysFont("bahnschrift", 25)


class SnakeInterface:
    def __init__(self):
        self.snake = snake.Snake()
        self.display = pygame.display.set_mode((self.snake.SCREEN_WIDTH, self.snake.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.close_window = False
        self.key_buffer = deque()

    def display_score(self):
        score_text = FONT_STYLE.render(f"Your Score: {self.snake.snake_length - 1}", True, BODY)
        self.display.blit(score_text, [10, 10])

    def draw_snake(self):
        if not self.snake.snake_positions:
            return  # Éviter l'erreur d'accès à une liste vide

        for segment in self.snake.snake_positions[:-1]:
            pygame.draw.rect(self.display, BODY,
                             [segment[0], segment[1], self.snake.SNAKE_BLOCK, self.snake.SNAKE_BLOCK])

        pygame.draw.rect(self.display, HEAD, [
            self.snake.snake_positions[-1][0], self.snake.snake_positions[-1][1],
            self.snake.SNAKE_BLOCK, self.snake.SNAKE_BLOCK
        ])

    def display_message(self, msg, color):
        mesg = FONT_STYLE.render(msg, True, color)
        self.display.blit(mesg, [self.snake.SCREEN_WIDTH / 6, self.snake.SCREEN_HEIGHT / 3])

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_window = True
            elif event.type == pygame.KEYDOWN:
                self.key_buffer.append(event.key)

    def process_key_buffer(self):
        if self.key_buffer:
            key = self.key_buffer.popleft()
            if key == pygame.K_LEFT and self.snake.displacement[0] == 0:
                self.snake.displacement = [-self.snake.SNAKE_BLOCK, 0]
            elif key == pygame.K_RIGHT and self.snake.displacement[0] == 0:
                self.snake.displacement = [self.snake.SNAKE_BLOCK, 0]
            elif key == pygame.K_UP and self.snake.displacement[1] == 0:
                self.snake.displacement = [0, -self.snake.SNAKE_BLOCK]
            elif key == pygame.K_DOWN and self.snake.displacement[1] == 0:
                self.snake.displacement = [0, self.snake.SNAKE_BLOCK]

    def play(self):
        while not self.close_window:
            self.handle_events()
            self.process_key_buffer()
            self.snake.process()

            if self.snake.game_over:
                self.display.fill(BACKGROUND)
                self.display_message("Game Over! Press R to Restart or Q to Quit", FRUIT)
                pygame.display.update()
                pygame.time.wait(2000)
                self.wait_for_restart()
                continue

            self.display.fill(BACKGROUND)
            pygame.draw.rect(self.display, FRUIT,
                             [self.snake.food_position[0], self.snake.food_position[1], self.snake.SNAKE_BLOCK,
                              self.snake.SNAKE_BLOCK])
            self.draw_snake()
            self.display_score()

            pygame.display.update()
            self.clock.tick(15)

        pygame.quit()
        quit()

    def wait_for_restart(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_window = True
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.close_window = True
                        return
                    elif event.key == pygame.K_r:
                        self.snake.__init__()
                        waiting = False


if __name__ == "__main__":
    game = SnakeInterface()
    game.play()
