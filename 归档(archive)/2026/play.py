import pygame
import numpy as np
import random
import math
from dataclasses import dataclass
from typing import List, Tuple

pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# 字体
try:
    font_paths = [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
    ]
    chinese_font = None
    for path in font_paths:
        try:
            chinese_font = pygame.font.Font(path, 16)
            break
        except:
            continue
    if chinese_font is None:
        chinese_font = pygame.font.Font(None, 16)
    font = chinese_font
except:
    font = pygame.font.Font(None, 16)

# ==================== 新功能：视觉效果 ====================
@dataclass
class Effect:
    x: float
    y: float
    color: Tuple[int, int, int]
    size: int
    life: float
    max_life: float
    effect_type: str  # 'explosion', 'ripple', 'trail'

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.effects = []
        
    def add_explosion(self, x, y, color, count=10):
        for _ in range(count):
            angle = random.uniform(0, math.pi*2)
            speed = random.uniform(2, 8)
            life = random.uniform(20, 60)
            
            self.effects.append(Effect(
                x, y,
                color,
                random.randint(3, 8),
                life, life,
                'explosion'
            ))
    
    def add_ripple(self, x, y, color):
        self.effects.append(Effect(
            x, y,
            color,
            5,
            120, 120,
            'ripple'
        ))
    
    def add_trail(self, x, y, color):
        if random.random() < 0.3:
            self.effects.append(Effect(
                x, y,
                color,
                random.randint(2, 4),
                30, 30,
                'trail'
            ))
    
    def update_effects(self):
        new_effects = []
        for e in self.effects:
            e.life -= 1
            
            if e.effect_type == 'explosion':
                e.x += random.uniform(-2, 2)
                e.y += random.uniform(-2, 2)
                e.size = max(1, e.size * 0.95)
            
            elif e.effect_type == 'ripple':
                e.size += 2
            
            if e.life > 0:
                new_effects.append(e)
        
        self.effects = new_effects
    
    def draw_effects(self, surface):
        for e in self.effects:
            alpha = int(255 * (e.life / e.max_life))
            
            if e.effect_type == 'trail':
                s = pygame.Surface((e.size*2, e.size*2), pygame.SRCALPHA)
                rgba_color = (e.color[0], e.color[1], e.color[2], alpha//2)
                pygame.draw.circle(s, rgba_color, 
                                 (e.size, e.size), e.size)
                surface.blit(s, (int(e.x-e.size), int(e.y-e.size)))
            
            else:
                s = pygame.Surface((e.size*2, e.size*2), pygame.SRCALPHA)
                rgba_color = (e.color[0], e.color[1], e.color[2], alpha)
                pygame.draw.circle(s, rgba_color, 
                                 (e.size, e.size), e.size, 
                                 1 if e.effect_type == 'ripple' else 0)
                surface.blit(s, (int(e.x-e.size), int(e.y-e.size)))

# ==================== 激进版粒子 ====================
@dataclass
class Particle:
    x: float
    y: float
    color_type: str
    size: int = 6
    vx: float = 0
    vy: float = 0
    
    def __post_init__(self):
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        
        # 更激进的能量系统
        if self.color_type == 'red':
            self.energy = 120.0
            self.max_energy = 120.0
        elif self.color_type == 'blue':
            self.energy = 120.0
            self.max_energy = 120.0
        elif self.color_type == 'black':
            self.energy = 200.0
            self.max_energy = 200.0
        else:  # white
            self.energy = 1000.0
            self.max_energy = 1000.0
        
        self.kill_count = 0 if self.color_type == 'black' else 0
        self.split_cooldown = 0  # 分裂冷却
        self.update_color()
    
    def update_color(self):
        energy_ratio = self.energy / self.max_energy
        
        if self.color_type == 'red':
            r = 255
            g = min(255, int(150 * energy_ratio))
            b = g
            self.color = (r, g, b)
            self.glow_color = (255, 200, 200)
            
        elif self.color_type == 'blue':
            r = min(255, int(150 * energy_ratio))
            g = r
            b = 255
            self.color = (r, g, b)
            self.glow_color = (200, 200, 255)
            
        elif self.color_type == 'black':
            dark = max(30, int(100 * energy_ratio))
            self.color = (dark, dark, dark)
            self.glow_color = (150, 150, 150)
            
        else:  # white
            bright = min(255, int(220 + 35 * energy_ratio))
            self.color = (bright, bright, bright)
            self.glow_color = (255, 255, 255)
    
    def distance_to(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)
    
    def move(self, white_centers=None, black_repulsion=False):
        if self.split_cooldown > 0:
            self.split_cooldown -= 1
        
        self.x += self.vx
        self.y += self.vy
        
        # 能量自然消耗（不同类型不同速率）
        if self.color_type == 'white':
            self.energy -= 0.5
        elif self.color_type == 'black':
            self.energy -= 0.1
        else:
            self.energy -= 0.05
        
        # 白球引力（更强）
        if white_centers:
            for wx, wy, power in white_centers:
                dx = wx - self.x
                dy = wy - self.y
                dist = max(10, math.hypot(dx, dy))
                
                # 距离越近引力越强
                force = power * 100 / (dist * 0.05)
                self.vx += (dx / dist) * force * 0.15
                self.vy += (dy / dist) * force * 0.15
        
        # 黑球数量过多时相互排斥
        if black_repulsion and self.color_type == 'black':
            # 额外的随机运动，避免僵化
            self.vx += random.uniform(-0.5, 0.5)
            self.vy += random.uniform(-0.5, 0.5)
        
        # 边界反弹
        margin = self.size
        if self.x < margin:
            self.x = margin
            self.vx = abs(self.vx) * 0.9
        elif self.x > WIDTH - margin:
            self.x = WIDTH - margin
            self.vx = -abs(self.vx) * 0.9
            
        if self.y < margin:
            self.y = margin
            self.vy = abs(self.vy) * 0.9
        elif self.y > HEIGHT - margin:
            self.y = HEIGHT - margin
            self.vy = -abs(self.vy) * 0.9
        
        # 速度限制
        speed = math.hypot(self.vx, self.vy)
        if speed > 8:
            self.vx *= 0.85
            self.vy *= 0.85
        
        self.update_color()
        
        # 死亡检查
        if self.energy <= 0:
            if self.color_type == 'black':
                self.color_type = 'white'
                self.energy = 800
                self.max_energy = 1000
                return True
            return False
        return True

# ==================== 混沌生态系统 ====================
class ChaoticEcosystem:
    def __init__(self):
        self.particles = []
        self.particle_system = ParticleSystem()
        self.time = 0
        
        # 更激进的初始配置
        for _ in range(15):
            self.particles.append(Particle(
                random.randint(100, WIDTH-100),
                random.randint(100, HEIGHT-100),
                'red'
            ))
            self.particles.append(Particle(
                random.randint(100, WIDTH-100),
                random.randint(100, HEIGHT-100),
                'blue'
            ))
        
        # 更多初始黑球
        for _ in range(4):
            self.particles.append(Particle(
                random.randint(100, WIDTH-100),
                random.randint(100, HEIGHT-100),
                'black'
            ))
        
        # 初始可能有一个白球
        if random.random() < 0.3:
            self.particles.append(Particle(
                WIDTH//2, HEIGHT//2,
                'white'
            ))
        
        self.stats = {
            'collisions': 0,
            'splits': 0,
            'kills': 0,
            'transformations': 0,
            'chain_reactions': 0
        }
        
        print("混沌生态系统启动！")
        print("警告：系统可能极端不稳定！")
    
    def get_white_centers(self):
        """获取白球位置和引力强度"""
        centers = []
        for p in self.particles:
            if p.color_type == 'white':
                # 白球能量越高，引力越强
                power = (p.energy / p.max_energy) * 2.0
                centers.append((p.x, p.y, power))
        return centers
    
    def apply_forces(self):
        """更强烈的力系统"""
        red_blue = [p for p in self.particles if p.color_type in ['red', 'blue']]
        blacks = [p for p in self.particles if p.color_type == 'black']
        
        # 红蓝之间的力（更强）
        for i, p1 in enumerate(red_blue):
            for p2 in red_blue[i+1:]:
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                dist = max(5, math.hypot(dx, dy))
                
                if dist < 200:  # 更大的作用范围
                    if p1.color_type != p2.color_type:
                        # 异色吸引（强烈）
                        force = 2.0 / (dist * 0.01)
                        dir_x, dir_y = dx/dist, dy/dist
                        
                        p1.vx += dir_x * force * 0.08
                        p1.vy += dir_y * force * 0.08
                        p2.vx -= dir_x * force * 0.08
                        p2.vy -= dir_y * force * 0.08
                    else:
                        # 同色斥力（但也可能转变为吸引，增加随机性）
                        if random.random() < 0.1:  # 10%概率反常吸引
                            force = 1.5 / (dist * 0.01)
                            dir_x, dir_y = dx/dist, dy/dist
                            p1.vx += dir_x * force * 0.05
                            p1.vy += dir_y * force * 0.05
                            p2.vx -= dir_x * force * 0.05
                            p2.vy -= dir_y * force * 0.05
                        else:
                            force = 1.0 / (dist * 0.01)
                            dir_x, dir_y = dx/dist, dy/dist
                            p1.vx -= dir_x * force * 0.06
                            p1.vy -= dir_y * force * 0.06
                            p2.vx += dir_x * force * 0.06
                            p2.vy += dir_y * force * 0.06
        
        # 黑球：更激进的狩猎
        for black in blacks:
            # 饥饿程度越高，狩猎越积极
            hunger = 1.0 - (black.energy / black.max_energy)
            
            targets = []
            for p in red_blue:
                dist = black.distance_to(p)
                if dist < 400:  # 更大的狩猎范围
                    # 虚弱的目标更有吸引力
                    target_value = (1.0 / dist) * (1.0 - p.energy/p.max_energy)
                    targets.append((p, dist, target_value))
            
            if targets:
                # 选择最有价值的目标
                targets.sort(key=lambda x: x[2], reverse=True)
                target = targets[0][0]
                
                dx = target.x - black.x
                dy = target.y - black.y
                dist = max(1, math.hypot(dx, dy))
                
                # 饥饿程度越高，速度越快
                hunt_power = 2.0 + hunger * 3.0
                black.vx += (dx / dist) * hunt_power * 0.25
                black.vy += (dy / dist) * hunt_power * 0.25
        
        # 黑球数量过多时的相互排斥
        black_count = len(blacks)
        red_blue_count = len(red_blue)
        if black_count > max(3, red_blue_count * 0.3):
            for black in blacks:
                for other in blacks:
                    if black is not other:
                        dx = other.x - black.x
                        dy = other.y - black.y
                        dist = max(5, math.hypot(dx, dy))
                        
                        if dist < 100:
                            force = 3.0 / (dist * 0.01)
                            black.vx -= (dx / dist) * force * 0.1
                            black.vy -= (dy / dist) * force * 0.1
    
    def check_collisions(self):
        """更暴力的碰撞系统"""
        to_remove = []
        to_add = []
        
        for i, p1 in enumerate(self.particles):
            for j, p2 in enumerate(self.particles[i+1:]):
                actual_j = i + 1 + j
                dist = p1.distance_to(p2)
                min_dist = p1.size + p2.size
                
                if dist < min_dist:
                    self.stats['collisions'] += 1
                    
                    # 更强烈的物理反弹
                    dx = p2.x - p1.x
                    dy = p2.y - p1.y
                    if dx == 0 and dy == 0:
                        dx, dy = 1, 0
                    
                    dist_vec = max(0.1, math.hypot(dx, dy))
                    nx, ny = dx/dist_vec, dy/dist_vec
                    
                    overlap = min_dist - dist + 1
                    p1.x -= overlap * nx * 0.5
                    p1.y -= overlap * ny * 0.5
                    p2.x += overlap * nx * 0.5
                    p2.y += overlap * ny * 0.5
                    
                    # 交换部分动量
                    temp_vx, temp_vy = p1.vx, p1.vy
                    p1.vx = p2.vx * 0.7
                    p1.vy = p2.vy * 0.7
                    p2.vx = temp_vx * 0.7
                    p2.vy = temp_vy * 0.7
                    
                    # 添加视觉效果
                    mid_x = (p1.x + p2.x) / 2
                    mid_y = (p1.y + p2.y) / 2
                    self.particle_system.add_explosion(
                        mid_x, mid_y, 
                        (150, 150, 255), 
                        5
                    )
                    
                    # 红蓝碰撞
                    if p1.color_type in ['red', 'blue'] and p2.color_type in ['red', 'blue']:
                        self.handle_red_blue_collision(p1, p2, to_add)
                    
                    # 黑球碰撞
                    elif 'black' in [p1.color_type, p2.color_type]:
                        self.handle_black_collision(p1, p2, to_remove, to_add)
                    
                    # 白球碰撞
                    elif 'white' in [p1.color_type, p2.color_type]:
                        self.handle_white_collision(p1, p2, to_remove)
        
        # 应用变更
        self.particles = [p for p in self.particles if p not in to_remove]
        self.particles.extend(to_add)
    
    def handle_red_blue_collision(self, p1, p2, to_add):
        """红蓝碰撞：可能连锁分裂"""
        if p1.color_type == p2.color_type:
            # 同色：高概率分裂
            if p1.split_cooldown == 0 and p2.split_cooldown == 0:
                split_chance = 0.6  # 60%概率
                
                # 能量越高，分裂概率越高
                split_chance += min(0.3, (p1.energy/p1.max_energy) * 0.3)
                split_chance += min(0.3, (p2.energy/p2.max_energy) * 0.3)
                
                if random.random() < split_chance:
                    # 可能分裂多个
                    split_count = random.randint(1, 3)
                    
                    for _ in range(split_count):
                        angle = random.uniform(0, math.pi*2)
                        distance = random.uniform(10, 30)
                        
                        new_x = (p1.x + p2.x)/2 + math.cos(angle) * distance
                        new_y = (p1.y + p2.y)/2 + math.sin(angle) * distance
                        
                        new_particle = Particle(new_x, new_y, p1.color_type)
                        new_particle.vx = (p1.vx + p2.vx)/2 + random.uniform(-2, 2)
                        new_particle.vy = (p1.vy + p2.vy)/2 + random.uniform(-2, 2)
                        new_particle.energy = (p1.energy + p2.energy) * 0.4 / split_count
                        new_particle.split_cooldown = 30  # 冷却时间
                        
                        to_add.append(new_particle)
                        self.stats['splits'] += 1
                    
                    # 母体损失能量
                    p1.energy *= 0.6
                    p2.energy *= 0.6
                    p1.split_cooldown = 45
                    p2.split_cooldown = 45
                    
                    # 视觉效果
                    self.particle_system.add_explosion(
                        (p1.x + p2.x)/2, (p1.y + p2.y)/2,
                        p1.color,
                        15
                    )
                    
                    # 连锁反应检查
                    if split_count >= 2 and random.random() < 0.3:
                        self.stats['chain_reactions'] += 1
                        print("💥 连锁分裂反应！")
        else:
            # 异色：能量交换更剧烈
            transfer = min(20, p1.energy * 0.2, p2.energy * 0.2)
            p1.energy -= transfer
            p2.energy += transfer
            
            # 可能触发能量爆发
            if transfer > 15:
                p1.vx += random.uniform(-3, 3)
                p1.vy += random.uniform(-3, 3)
                p2.vx += random.uniform(-3, 3)
                p2.vy += random.uniform(-3, 3)
    
    def handle_black_collision(self, p1, p2, to_remove, to_add):
        """黑球吞噬：更暴力"""
        black = p1 if p1.color_type == 'black' else p2
        other = p2 if p1.color_type == 'black' else p1
        
        if other.color_type in ['red', 'blue']:
            # 吞噬
            energy_gain = other.energy * 0.8  # 吸收80%
            black.energy = min(black.max_energy, black.energy + energy_gain)
            black.kill_count += 1
            
            # 爆炸效果
            self.particle_system.add_explosion(
                other.x, other.y,
                (255, 100, 100) if other.color_type == 'red' else (100, 100, 255),
                20
            )
            
            to_remove.append(other)
            self.stats['kills'] += 1
            
            # 黑球可能暴力分裂
            black_count = len([p for p in self.particles if p.color_type == 'black'])
            red_blue_count = len([p for p in self.particles if p.color_type in ['red', 'blue']])
            
            # 分裂条件更宽松
            target_black = max(2, int(red_blue_count * 0.25))
            
            if black_count < target_black and black.kill_count >= 2:
                split_chance = 0.5 + (black.kill_count - 2) * 0.2
                
                if random.random() < split_chance:
                    # 分裂1-3个新黑球
                    split_num = random.randint(1, 3)
                    
                    for i in range(split_num):
                        angle = math.pi * 2 * i / split_num + random.uniform(-0.5, 0.5)
                        distance = random.uniform(15, 40)
                        
                        new_x = black.x + math.cos(angle) * distance
                        new_y = black.y + math.sin(angle) * distance
                        
                        new_black = Particle(new_x, new_y, 'black')
                        new_black.vx = black.vx * 0.8 + random.uniform(-2, 2)
                        new_black.vy = black.vy * 0.8 + random.uniform(-2, 2)
                        new_black.energy = black.energy * 0.3
                        new_black.kill_count = black.kill_count // 2
                        
                        to_add.append(new_black)
                    
                    black.energy *= 0.4
                    black.kill_count = 0
                    
                    print(f"⚫ 黑球暴力分裂成{split_num}个！")
    
    def handle_white_collision(self, p1, p2, to_remove):
        """白球碰撞：吸收一切"""
        white = p1 if p1.color_type == 'white' else p2
        other = p2 if p1.color_type == 'white' else p1
        
        if other.color_type == 'black':
            # 白球吸收黑球
            white.energy += other.energy * 1.5
            to_remove.append(other)
            self.stats['transformations'] += 1
            
            self.particle_system.add_ripple(
                white.x, white.y,
                (255, 255, 200)
            )
            
            # 白球可能释放能量波
            if white.energy > white.max_energy * 0.8:
                self.create_energy_wave(white.x, white.y)
                white.energy *= 0.7
                
        elif other.color_type in ['red', 'blue']:
            # 白球消灭红蓝
            white.energy += other.energy * 0.2
            to_remove.append(other)
            
            self.particle_system.add_explosion(
                other.x, other.y,
                other.color,
                8
            )
    
    def create_energy_wave(self, x, y):
        """创建能量冲击波"""
        print("🌊 白球能量爆发！")
        
        # 给所有粒子一个向外推的力
        for p in self.particles:
            if p is not None:
                dx = p.x - x
                dy = p.y - y
                dist = max(10, math.hypot(dx, dy))
                
                if dist < 300:
                    force = 50.0 / dist
                    p.vx += (dx / dist) * force * 0.5
                    p.vy += (dy / dist) * force * 0.5
        
        # 视觉效果
        for i in range(5):
            radius = 50 + i * 60
            self.particle_system.add_ripple(x, y, (255, 255, 200))
    
    def update(self):
        """更新系统"""
        self.time += 1
        
        # 更新粒子系统效果
        self.particle_system.update_effects()
        
        # 每帧添加一些拖尾效果
        for p in self.particles:
            if random.random() < 0.1:
                self.particle_system.add_trail(p.x, p.y, p.color)
        
        # 获取白球信息
        white_centers = self.get_white_centers()
        
        # 检查是否需要黑球排斥
        black_count = len([p for p in self.particles if p.color_type == 'black'])
        red_blue_count = len([p for p in self.particles if p.color_type in ['red', 'blue']])
        black_repulsion = black_count > max(3, red_blue_count * 0.35)
        
        # 应用力系统
        self.apply_forces()
        
        # 移动粒子
        alive_particles = []
        for p in self.particles:
            if p.move(white_centers, black_repulsion):
                alive_particles.append(p)
        self.particles = alive_particles
        
        # 碰撞检测
        self.check_collisions()
        
        # 偶尔随机事件
        if self.time % 180 == 0 and random.random() < 0.3:
            self.random_event()
    
    def random_event(self):
        """随机事件增加趣味性"""
        events = [
            self.event_energy_surge,
            self.event_color_inversion,
            self.event_black_hole,
            self.event_reproduction_frenzy
        ]
        
        if random.random() < 0.4:  # 40%概率触发事件
            event = random.choice(events)
            event()
    
    def event_energy_surge(self):
        """能量爆发事件"""
        print("⚡ 能量爆发！所有粒子加速！")
        for p in self.particles:
            p.vx *= 1.5
            p.vy *= 1.5
            p.energy = min(p.max_energy, p.energy * 1.2)
    
    def event_color_inversion(self):
        """颜色反转事件"""
        print("🎨 颜色反转！红蓝互换！")
        for p in self.particles:
            if p.color_type == 'red':
                p.color_type = 'blue'
            elif p.color_type == 'blue':
                p.color_type = 'red'
            p.update_color()
    
    def event_black_hole(self):
        """黑洞事件：创建一个临时的超强引力点"""
        print("🌀 临时黑洞出现！")
        x, y = random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100)
        
        # 给所有粒子一个朝向黑洞的力
        for p in self.particles:
            dx = x - p.x
            dy = y - p.y
            dist = max(10, math.hypot(dx, dy))
            
            if dist < 400:
                force = 200.0 / (dist * 0.01)
                p.vx += (dx / dist) * force * 0.02
                p.vy += (dy / dist) * force * 0.02
        
        # 视觉效果
        for i in range(3):
            self.particle_system.add_ripple(x, y, (100, 100, 200))
    
    def event_reproduction_frenzy(self):
        """繁殖狂热事件"""
        print("🐇 繁殖狂热！红蓝分裂率提高！")
        # 这个效果会在碰撞处理中自然体现
    
    def draw(self, surface):
        """绘制系统"""
        # 动态背景（根据系统活跃度）
        red_blue_count = len([p for p in self.particles if p.color_type in ['red', 'blue']])
        black_count = len([p for p in self.particles if p.color_type == 'black'])
        
        bg_r = min(30, red_blue_count // 2)
        bg_g = min(30, black_count * 3)
        bg_b = 40
        surface.fill((bg_r, bg_g, bg_b))
        
        # 绘制引力场
        for p in self.particles:
            if p.color_type == 'white':
                # 白色引力场
                for radius in range(30, 181, 30):
                    alpha = max(20, 80 - radius//2)
                    s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    color = (200, 230, 255, alpha) if p.energy > 500 else (255, 230, 200, alpha)
                    pygame.draw.circle(s, color, 
                                     (radius, radius), radius, 2)
                    surface.blit(s, (int(p.x-radius), int(p.y-radius)))
            
            elif p.color_type == 'black':
                # 黑色狩猎范围
                if p.energy < p.max_energy * 0.5:
                    radius = 50
                    s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (255, 100, 100, 30), 
                                     (radius, radius), radius)
                    surface.blit(s, (int(p.x-radius), int(p.y-radius)))
        
        # 绘制特效
        self.particle_system.draw_effects(surface)
        
        # 绘制粒子
        for p in self.particles:
            # 光晕
            glow_radius = p.size + 3
            for i in range(4):
                radius = glow_radius + i
                alpha = 60 - i*15
                s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                glow_rgba = (p.glow_color[0], p.glow_color[1], p.glow_color[2], alpha)
                pygame.draw.circle(s, glow_rgba, 
                                 (radius, radius), radius)
                surface.blit(s, (int(p.x-radius), int(p.y-radius)))
            
            # 主体
            pygame.draw.circle(surface, p.color, 
                             (int(p.x), int(p.y)), p.size)
            
            # 能量条（更明显）
            if p.color_type in ['red', 'blue', 'black']:
                bar_width = 24
                bar_height = 4
                bar_x = int(p.x - bar_width/2)
                bar_y = int(p.y - p.size - 8)
                
                # 背景
                pygame.draw.rect(surface, (40, 40, 40), 
                               (bar_x, bar_y, bar_width, bar_height), 1)
                
                # 填充
                fill_width = int(bar_width * (p.energy / p.max_energy))
                if p.color_type == 'black':
                    fill_color = (220, 220, 220) if p.energy > 100 else (255, 150, 150)
                elif p.color_type == 'red':
                    fill_color = (255, 120, 120)
                else:
                    fill_color = (120, 120, 255)
                
                pygame.draw.rect(surface, fill_color,
                               (bar_x, bar_y, fill_width, bar_height))
        
        # 绘制UI
        self.draw_ui(surface)
    
    def draw_ui(self, surface):
        """绘制用户界面"""
        counts = {'red': 0, 'blue': 0, 'black': 0, 'white': 0}
        for p in self.particles:
            counts[p.color_type] += 1
        
        total = sum(counts.values())
        red_blue = counts['red'] + counts['blue']
        
        # 背景面板
        pygame.draw.rect(surface, (10, 10, 30, 220), (10, 10, 400, 250), 0, 10)
        pygame.draw.rect(surface, (30, 30, 60, 200), (10, 10, 400, 250), 2, 10)
        
        # 标题
        title = font.render("⚡ 混沌引力生态系统 ⚡", True, (255, 255, 180))
        surface.blit(title, (20, 20))
        
        # 数量显示
        count_text = [
            f"时间: {self.time//60}:{self.time%60:02d}",
            f"红球: {counts['red']:3d}   蓝球: {counts['blue']:3d}",
            f"黑球: {counts['black']:3d}   白球: {counts['white']:3d}",
            f"总数: {total:3d}   活跃度: {red_blue//2 + counts['black']*5}",
            "",
            "=== 动态统计 ===",
            f"碰撞: {self.stats['collisions']:6d}",
            f"分裂: {self.stats['splits']:6d}  吞噬: {self.stats['kills']:6d}",
            f"转化: {self.stats['transformations']:4d}  连锁: {self.stats['chain_reactions']:3d}",
            "",
            "=== 系统状态 ===",
        ]
        
        for i, text in enumerate(count_text):
            color = (220, 240, 255) if i < 4 else (200, 255, 200) if i >= 5 else (200, 220, 200)
            text_surface = font.render(text, True, color)
            surface.blit(text_surface, (20, 50 + i * 22))
        
        # 系统警告
        if counts['black'] > red_blue * 0.3:
            warning = font.render("⚠️ 警告：黑球数量过多！", True, (255, 100, 100))
            surface.blit(warning, (20, 240))
        elif red_blue < 10:
            warning = font.render("⚠️ 警告：红蓝球濒临灭绝！", True, (255, 200, 100))
            surface.blit(warning, (20, 240))
        
        # 控制提示
        controls = [
            "控制: P暂停 R重置 A加红蓝 B加黑 W加白",
            "      SPACE手动碰撞 C清空白球"
        ]
        for i, text in enumerate(controls):
            text_surface = font.render(text, True, (180, 230, 180))
            surface.blit(text_surface, (WIDTH//2 - 200, HEIGHT - 40 + i * 22))

# ==================== 主程序 ====================
def main():
    ecosystem = ChaoticEcosystem()
    running = True
    paused = False
    
    print("\n=== 控制说明 ===")
    print("P - 暂停/继续")
    print("R - 重置系统")
    print("A - 添加红蓝球各1个")
    print("B - 添加黑球1个")
    print("W - 添加白球1个（最多2个）")
    print("SPACE - 手动触发碰撞测试")
    print("C - 清除所有白球")
    print("E - 触发随机事件")
    print("=" * 30)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    print("⏸️ 暂停" if paused else "▶️ 继续")
                
                elif event.key == pygame.K_r:
                    ecosystem = ChaoticEcosystem()
                    print("🔄 系统重置")
                
                elif event.key == pygame.K_a:
                    ecosystem.particles.append(Particle(
                        random.randint(50, WIDTH-50),
                        random.randint(50, HEIGHT-50),
                        'red'
                    ))
                    ecosystem.particles.append(Particle(
                        random.randint(50, WIDTH-50),
                        random.randint(50, HEIGHT-50),
                        'blue'
                    ))
                    print("➕ 添加红蓝球各1个")
                
                elif event.key == pygame.K_b:
                    ecosystem.particles.append(Particle(
                        random.randint(50, WIDTH-50),
                        random.randint(50, HEIGHT-50),
                        'black'
                    ))
                    print("⚫ 添加黑球1个")
                
                elif event.key == pygame.K_w:
                    white_count = len([p for p in ecosystem.particles 
                                     if p.color_type == 'white'])
                    if white_count < 2:
                        ecosystem.particles.append(Particle(
                            random.randint(50, WIDTH-50),
                            random.randint(50, HEIGHT-50),
                            'white'
                        ))
                        print("⚪ 添加白球1个")
                    else:
                        print("⚠️ 白球已达上限2个")
                
                elif event.key == pygame.K_SPACE:
                    reds = [p for p in ecosystem.particles 
                           if p.color_type == 'red']
                    if len(reds) >= 2:
                        reds[0].x = reds[1].x + 20
                        reds[0].y = reds[1].y
                        print("💥 手动触发碰撞测试")
                
                elif event.key == pygame.K_c:
                    whites = [p for p in ecosystem.particles 
                             if p.color_type == 'white']
                    for w in whites:
                        ecosystem.particles.remove(w)
                    print("🧹 清除所有白球")
                
                elif event.key == pygame.K_e:
                    ecosystem.random_event()
                    print("🎲 手动触发随机事件")
        
        if not paused:
            ecosystem.update()
        
        ecosystem.draw(screen)
        
        if paused:
            pause_text = font.render("PAUSED", True, (255, 50, 50))
            screen.blit(pause_text, (WIDTH//2 - 40, HEIGHT//2))
        
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (200, 200, 200))
        screen.blit(fps_text, (WIDTH - 100, 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    
    # 最终报告
    print("\n" + "="*50)
    print("混沌模拟结束！")
    
    counts = {'red': 0, 'blue': 0, 'black': 0, 'white': 0}
    for p in ecosystem.particles:
        counts[p.color_type] += 1
    
    print(f"运行时间: {ecosystem.time}帧 ({ecosystem.time//60}秒)")
    print(f"最终数量: 红{counts['red']} 蓝{counts['blue']} 黑{counts['black']} 白{counts['white']}")
    print(f"总碰撞: {ecosystem.stats['collisions']}")
    print(f"总分裂: {ecosystem.stats['splits']} (连锁: {ecosystem.stats['chain_reactions']})")
    print(f"总吞噬: {ecosystem.stats['kills']}")
    print(f"总转化: {ecosystem.stats['transformations']}")
    
    if counts['red'] == 0 and counts['blue'] == 0:
        print("💀 红蓝球完全灭绝！")
    elif counts['black'] == 0:
        print("🕊️ 黑球完全消失！")
    elif counts['white'] >= 2:
        print("🌌 双白球引力奇点形成！")
    
    print("="*50)

if __name__ == "__main__":
    main()