import pygame

# 初始化 Pygame
pygame.init()

# 窗口尺寸
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("矩阵游戏")

# 网格和角色属性
CELL_SIZE = 40
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE
player_pos = [3, 3]
WHITE, BLACK, RED = (255, 255, 255), (0, 0, 0), (255, 0, 0)

# 游戏主循环
running = True
clock = pygame.time.Clock()
while running:
    screen.fill(WHITE)

    # 绘制网格
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)

    # 绘制玩家
    pygame.draw.rect(screen, RED, (
        player_pos[1] * CELL_SIZE,
        player_pos[0] * CELL_SIZE,
        CELL_SIZE, CELL_SIZE
    ))

    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and player_pos[0] > 0:
                player_pos[0] -= 1
            elif event.key == pygame.K_s and player_pos[0] < ROWS - 1:
                player_pos[0] += 1
            elif event.key == pygame.K_a and player_pos[1] > 0:
                player_pos[1] -= 1
            elif event.key == pygame.K_d and player_pos[1] < COLS - 1:
                player_pos[1] += 1

    # 刷新屏幕
    pygame.display.flip()
    clock.tick(10)

pygame.quit()
