import pygame
import random
import sys
from collections import deque

# 常量设置
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
GRID_SIZE = 20
FPS = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# 方向枚举
class Direction:
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    UP = (0, -1)

# 坐标类
class Coor:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

# 蛇类
class Snake:
    def __init__(self):
        self.body = deque([Coor(5, 5)])  # 初始长度为1
        self.direction = Direction.RIGHT
        self.grow = False

    def move(self):
        head = self.body[0]
        new_head = Coor(head.x + self.direction[0], head.y + self.direction[1])

        if not self.grow:
            self.body.pop()  # 移除尾部
        else:
            self.grow = False

        self.body.appendleft(new_head)  # 插入新头部

    def change_direction(self, new_direction):
        # 防止逆向移动
        if (new_direction[0] + self.direction[0] == 0 and
                new_direction[1] + self.direction[1] == 0):
            return
        self.direction = new_direction

# 食物类
class Food:
    def __init__(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height
        self.position = None

    def spawn(self, snake_body):
        while True:
            x = random.randint(0, self.map_width - 1)
            y = random.randint(0, self.map_height - 1)
            self.position = Coor(x, y)
            if self.position not in snake_body:
                break

# 游戏类
class SnakeGame:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("贪吃蛇游戏")
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.food = Food(WINDOW_WIDTH // GRID_SIZE, WINDOW_HEIGHT // GRID_SIZE)
        self.food.spawn(self.snake.body)
        self.running = True

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.window, WHITE, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.window, WHITE, (0, y), (WINDOW_WIDTH, y))

    def draw_snake(self):
        for segment in self.snake.body:
            x, y = segment.x * GRID_SIZE, segment.y * GRID_SIZE
            pygame.draw.rect(self.window, GREEN, (x, y, GRID_SIZE, GRID_SIZE))

    def draw_food(self):
        x, y = self.food.position.x * GRID_SIZE, self.food.position.y * GRID_SIZE
        pygame.draw.rect(self.window, RED, (x, y, GRID_SIZE, GRID_SIZE))

    def check_collision(self):
        head = self.snake.body[0]
        # 撞墙
        if head.x < 0 or head.x >= WINDOW_WIDTH // GRID_SIZE or head.y < 0 or head.y >= WINDOW_HEIGHT // GRID_SIZE:
            return True
        # 撞自己
        if head in list(self.snake.body)[1:]:
            return True
        return False

    def check_food(self):
        if self.snake.body[0] == self.food.position:
            self.snake.grow = True
            self.food.spawn(self.snake.body)

    def game_over(self):
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over", True, RED)
        self.window.blit(text, (WINDOW_WIDTH // 4, WINDOW_HEIGHT // 3))
        pygame.display.flip()
        pygame.time.wait(2000)
        self.running = False

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.snake.change_direction(Direction.UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(Direction.DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(Direction.RIGHT)

            self.snake.move()
            if self.check_collision():
                self.game_over()
            self.check_food()

            # 绘制游戏
            self.window.fill(BLACK)
            self.draw_grid()
            self.draw_snake()
            self.draw_food()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
