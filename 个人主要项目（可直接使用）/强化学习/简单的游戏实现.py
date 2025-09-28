# import pynput
# from pynput.keyboard import Key, Listener
# import numpy as np
# import time
# import os
# import random

# class BreakoutGame:
#     def __init__(self):
#         # 游戏地图大小
#         self.width, self.height = 50, 20
#         self.game_map = np.zeros((self.height, self.width))
        
#         # 玩家挡板位置和大小
#         self.paddle_x = self.width // 2
#         self.paddle_y = self.height - 2
#         self.paddle_size = 7
        
#         # 球的位置和速度
#         self.ball_x = self.width // 2
#         self.ball_y = self.height - 4
#         self.ball_dx = 1
#         self.ball_dy = -1
        
#         # 砖块位置
#         self.bricks = []
#         self.init_bricks()
        
#         self.running = True
#         self.score = 0
        
#         # 更新游戏元素位置
#         self.update_game_elements()
        
#     def init_bricks(self):
#         # 初始化砖块，创建几行砖块
#         for y in range(3, 7):
#             for x in range(5, self.width - 5, 3):
#                 self.bricks.append([x, y])
    
#     def update_game_elements(self):
#         # 清空地图
#         self.game_map = np.zeros((self.height, self.width))
        
#         # 绘制挡板
#         for i in range(self.paddle_size):
#             paddle_pos = self.paddle_x + i - self.paddle_size // 2
#             if 0 <= paddle_pos < self.width:
#                 self.game_map[self.paddle_y, paddle_pos] = 1
        
#         # 绘制球
#         if 0 <= int(self.ball_x) < self.width and 0 <= int(self.ball_y) < self.height:
#             self.game_map[int(self.ball_y), int(self.ball_x)] = 2
            
#         # 绘制砖块
#         for brick in self.bricks:
#             x, y = brick
#             if 0 <= x < self.width and 0 <= y < self.height:
#                 self.game_map[y, x] = 3
    
#     def move_ball(self):
#         # 移动球
#         new_x = self.ball_x + self.ball_dx
#         new_y = self.ball_y + self.ball_dy
        
#         # 边界碰撞检测
#         if new_x <= 0 or new_x >= self.width - 1:
#             self.ball_dx = -self.ball_dx
#             new_x = self.ball_x + self.ball_dx
            
#         if new_y <= 0:
#             self.ball_dy = -self.ball_dy
#             new_y = self.ball_y + self.ball_dy
            
#         # 挡板碰撞检测
#         if int(new_y) == self.paddle_y:
#             paddle_start = self.paddle_x - self.paddle_size // 2
#             paddle_end = self.paddle_x + self.paddle_size // 2
#             if paddle_start <= int(new_x) <= paddle_end:
#                 self.ball_dy = -self.ball_dy
#                 # 根据击球位置改变球的方向
#                 hit_pos = (int(new_x) - paddle_start) / self.paddle_size
#                 self.ball_dx = (hit_pos - 0.5) * 2  # -1 到 1 之间
#                 new_y = self.ball_y + self.ball_dy
        
#         # 砖块碰撞检测
#         ball_int_x, ball_int_y = int(new_x), int(new_y)
#         for i, brick in enumerate(self.bricks):
#             brick_x, brick_y = brick
#             if brick_x == ball_int_x and brick_y == ball_int_y:
#                 # 移除砖块
#                 self.bricks.pop(i)
#                 self.score += 10
#                 self.ball_dy = -self.ball_dy
#                 break
        
#         # 更新球的位置
#         self.ball_x = new_x
#         self.ball_y = new_y
        
#         # 检查游戏是否结束（球掉出底部）
#         if self.ball_y >= self.height:
#             return False
#         return True
    
#     def on_press(self, key):
#         try:
#             if key == Key.left:
#                 self.paddle_x = max(self.paddle_size // 2, self.paddle_x - 2)
#             elif key == Key.right:
#                 self.paddle_x = min(self.width - self.paddle_size // 2 - 1, self.paddle_x + 2)
#             elif key == Key.esc:
#                 self.running = False
#                 return False
                
#             # 移动球
#             if self.running:
#                 ball_alive = self.move_ball()
#                 if not ball_alive:
#                     os.system('cls' if os.name == 'nt' else 'clear')
#                     print("游戏结束！")
#                     print(f"最终得分: {self.score}")
#                     self.running = False
#                     return False
                
#                 # 更新显示
#                 self.update_game_elements()
#                 self.display_game()
                
#         except AttributeError:
#             pass
    
#     def on_release(self, key):
#         if key == Key.esc:
#             self.running = False
#             return False
    
#     def display_game(self):
#         # 清屏
#         os.system('cls' if os.name == 'nt' else 'clear')
        
#         # 显示游戏地图
#         print("打砖块游戏 - 使用左右方向键移动挡板，ESC退出")
#         print("=" * (self.width + 2))
        
#         for y in range(self.height):
#             print("|", end="")
#             for x in range(self.width):
#                 if self.game_map[y, x] == 1:
#                     print("=", end="")  # 挡板
#                 elif self.game_map[y, x] == 2:
#                     print("O", end="")  # 球
#                 elif self.game_map[y, x] == 3:
#                     print("#", end="")  # 砖块
#                 else:
#                     print(" ", end="")  # 空地
#             print("|")
        
#         print("=" * (self.width + 2))
#         print(f"得分: {self.score}")
#         print(f"剩余砖块: {len(self.bricks)}")
        
#         if len(self.bricks) == 0:
#             print("恭喜！你清除了所有砖块！")
#             self.running = False
    
#     def start_listening(self):
#         # 初始显示
#         self.display_game()
#         print("\n游戏开始！使用左右方向键移动挡板。")
        
#         # 启动键盘监听
#         with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
#             listener.join()

#     def run(self):
#         """
#         游戏主循环
#         """
#         self.start_listening()

# # 使用方法
# if __name__ == "__main__":
#     game = BreakoutGame()
#     game.run()



# 现代游戏通常结合事件驱动和主循环
import pygame

class ModernGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 游戏对象
        self.player = Player()
        self.enemies = []
        
    def handle_events(self):
        """处理所有事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # 处理其他按键事件
                self.player.handle_key_down(event.key)
            elif event.type == pygame.KEYUP:
                self.player.handle_key_up(event.key)
                
    def update(self, dt):
        """更新游戏状态"""
        self.player.update(dt)
        for enemy in self.enemies:
            enemy.update(dt)
        self.check_collisions()
        
    def render(self):
        """渲染游戏画面"""
        self.screen.fill((0, 0, 0))
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        pygame.display.flip()
        
    def run(self):
        """主游戏循环"""
        while self.running:
            # 处理事件
            self.handle_events()
            
            # 计算时间差
            dt = self.clock.tick(60) / 1000.0  # 60 FPS
            
            # 更新游戏状态
            self.update(dt)
            
            # 渲染画面
            self.render()