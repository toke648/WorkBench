#!/usr/bin/env python3
"""
raycaster_ascii_v3.py
Upgraded ASCII raycaster with:
 - start screen, game over screen, restart
 - player HP, enemy HP, enemy melee damage with cooldown
 - enemies no longer "vanish" unexpectedly (HP-based death)
 - simultaneous key presses via background input thread
 - DDA raycasting, floor casting, sprite occlusion, bullet visualization

Controls:
  W/S - forward/back
  A/D - strafe left/right
  Left/Right arrows - turn left / turn right
  Space - shoot
  Q - quit (in game), R - restart at game over

  # -------------------- GAME LOGIC --------------------
  模拟 德国总部3D ASCII游戏实现
  - AI 辅助生成
  - 提示词暂未开源
"""

from math import sin, cos, tan, pi, sqrt, atan2
import time, os, sys, threading, random
import colorama, pyfiglet


# -------------------- CONFIG --------------------
SCREEN_WIDTH = 135
SCREEN_HEIGHT = 25
FOV = pi / 3.2
DEPTH = 20.0
FPS_TARGET = 30.0

MOVE_SPEED = 2.0      # forward/back units per second
STRAFE_SPEED = 3.1
TURN_SPEED = 1.7       # radians/sec

PLAYER_RADIUS = 0.22

ENEMY_COUNT = 6
PATROL_POINTS = 3

# damage / hp
PLAYER_MAX_HP = 500
ENEMY_MAX_HP = 200
ENEMY_MELEE_DAMAGE = 40
ENEMY_MELEE_RANGE = 0.9
ENEMY_MELEE_COOLDOWN = 1.0  # seconds between attacks
PLAYER_SHOT_DAMAGE = 120

# map legend:
# '#' wall, '.' empty, 'S' player spawn, 'E' enemy spawn
RAW_MAP = [
"############################",
"#......#...........#.......#",
"#......#...###.....#...E...#",
"#......#...#.......#.......#",
"#..S...#...###.....#.......#",
"#......#...........#.......#",
"#......#####.##########....#",
"#.......................#..#",
"#......#..............E.#..#",
"#......#..######.........#.#",
"#......#..#....#.....#....E#",
"#..E...#..#..........#.....#",
"#......#..#....#.....#.....#",
"#......#..######.....#.....#",
"#......#..............#....#",
"#..S...#...........S..#....#",
"############################"
]
MAP_W = len(RAW_MAP[0])
MAP_H = len(RAW_MAP)

# -------------------- PLATFORM INPUT (background thread) --------------------
KEYS_DOWN = set()
KEYS_LOCK = threading.Lock()
STOP_INPUT_THREAD = False

try:
    import msvcrt
    PLATFORM = 'windows'
    def _input_thread_windows():
        global STOP_INPUT_THREAD
        while not STOP_INPUT_THREAD:
            while msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch in (b'\x00', b'\xe0'):
                    code = msvcrt.getch()
                    if code == b'K': token = 'LEFT'
                    elif code == b'M': token = 'RIGHT'
                    elif code == b'H': token = 'UP'
                    elif code == b'P': token = 'DOWN'
                    else: token = None
                    if token:
                        with KEYS_LOCK: KEYS_DOWN.add(token)
                else:
                    try:
                        s = ch.decode('utf-8').lower()
                    except:
                        s = ''
                    if s:
                        with KEYS_LOCK: KEYS_DOWN.add(s)
            time.sleep(0.01)
    def input_thread_fn():
        _input_thread_windows()
except ImportError:
    import termios, tty, select
    PLATFORM = 'unix'
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    def _input_thread_unix():
        global STOP_INPUT_THREAD
        while not STOP_INPUT_THREAD:
            dr, _, _ = select.select([sys.stdin], [], [], 0)
            if dr:
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    dr2, _, _ = select.select([sys.stdin], [], [], 0.001)
                    if dr2:
                        c2 = sys.stdin.read(1)
                        if c2 == '[':
                            c3 = sys.stdin.read(1)
                            if c3 == 'D': token = 'LEFT'
                            elif c3 == 'C': token = 'RIGHT'
                            elif c3 == 'A': token = 'UP'
                            elif c3 == 'B': token = 'DOWN'
                            else: token = None
                            if token:
                                with KEYS_LOCK:
                                    KEYS_DOWN.add(token)
                    else:
                        with KEYS_LOCK: KEYS_DOWN.add('\x1b')
                else:
                    with KEYS_LOCK: KEYS_DOWN.add(ch.lower())
            time.sleep(0.005)
    def input_thread_fn():
        _input_thread_unix()

KEY_TIMESTAMP = {}
KEY_EXPIRY = 0.14
def start_input_thread():
    t = threading.Thread(target=input_thread_fn, daemon=True)
    t.start()
    return t
def refresh_key_states():
    now = time.time()
    with KEYS_LOCK:
        to_remove = []
        for k in list(KEYS_DOWN):
            KEY_TIMESTAMP[k] = now
            to_remove.append(k)
        for k in to_remove:
            if k in KEYS_DOWN: KEYS_DOWN.remove(k)
    expired = [k for k,ts in KEY_TIMESTAMP.items() if now - ts > KEY_EXPIRY]
    for k in expired:
        del KEY_TIMESTAMP[k]
def key_is_down(token):
    return token in KEY_TIMESTAMP

# -------------------- MAP / WORLD --------------------
grid = [[1 if RAW_MAP[y][x] == '#' else 0 for x in range(MAP_W)] for y in range(MAP_H)]
spawn_points = []
enemy_spawns = []
for yrow, row in enumerate(RAW_MAP):
    for xcol, ch in enumerate(row):
        if ch == 'S': spawn_points.append((xcol + 0.5, yrow + 0.5))
        if ch == 'E': enemy_spawns.append((xcol + 0.5, yrow + 0.5))
if not spawn_points: spawn_points = [(2.5,2.5)]

# -------------------- GAME STATE & ENTITIES --------------------
def reset_world():
    global player_x, player_y, player_angle, player_hp, score, bullets, sprites, game_state
    player_x, player_y = random.choice(spawn_points)
    player_angle = 0.4
    player_hp = PLAYER_MAX_HP
    score = 0
    bullets = []
    # spawn enemies with HP and melee cooldown
    sprites = []
    all_spawn_list = enemy_spawns[:] + [(random.uniform(3, MAP_W-3), random.uniform(3, MAP_H-3)) for _ in range(ENEMY_COUNT*2)]
    random.shuffle(all_spawn_list)
    for i in range(ENEMY_COUNT):
        sx, sy = all_spawn_list[i % len(all_spawn_list)]
        patrols = []
        for _ in range(PATROL_POINTS):
            for _try in range(40):
                rx = sx + random.uniform(-4,4); ry = sy + random.uniform(-4,4)
                if 1 < rx < MAP_W-1 and 1 < ry < MAP_H-1 and grid[int(ry)][int(rx)] == 0:
                    patrols.append((rx, ry)); break
        if not patrols: patrols = [(sx,sy)]
        sprites.append({
            'x': sx, 'y': sy, 'hp': ENEMY_MAX_HP, 'alive': True, 'char': 'M',
            'state': 'patrol', 'patrol': patrols, 'pi':0, 'speed': 1.6 + random.random()*0.8,
            'detect': 6.5, 'last_shot_flash':0.0, 'melee_cd':0.0
        })
    game_state = 'menu'  # menu -> playing -> gameover

reset_world()

# -------------------- RENDER SETTINGS --------------------
WALL_SHADES = ['█','▓','▒','░','.']
FLOOR_SHADES = ['·',',','-','_']
CEILING_CHAR = ' '
depth_buffer = [0.0] * SCREEN_WIDTH

def clear_screen():
    if os.name == 'nt': os.system('cls')
    else: sys.stdout.write('\x1b[2J\x1b[H')

def clamp(v,a,b): return max(a, min(b, v))
def is_wall(xi, yi):
    if xi < 0 or yi < 0 or xi >= MAP_W or yi >= MAP_H: return True
    return grid[int(yi)][int(xi)] == 1

# -------------------- DDA RAYCAST --------------------
def cast_single_ray(ray_x, ray_y, dir_x, dir_y):
    map_x = int(ray_x); map_y = int(ray_y)
    delta_dist_x = 1e30 if dir_x==0 else abs(1.0/dir_x)
    delta_dist_y = 1e30 if dir_y==0 else abs(1.0/dir_y)
    if dir_x < 0:
        step_x = -1; side_dist_x = (ray_x - map_x) * delta_dist_x
    else:
        step_x = 1; side_dist_x = (map_x + 1.0 - ray_x) * delta_dist_x
    if dir_y < 0:
        step_y = -1; side_dist_y = (ray_y - map_y) * delta_dist_y
    else:
        step_y = 1; side_dist_y = (map_y + 1.0 - ray_y) * delta_dist_y
    hit = False; side = 0; steps=0; max_steps=300
    while not hit and steps < max_steps:
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x; map_x += step_x; side = 0
        else:
            side_dist_y += delta_dist_y; map_y += step_y; side = 1
        if map_x < 0 or map_y < 0 or map_x >= MAP_W or map_y >= MAP_H:
            hit = True; break
        if grid[map_y][map_x] == 1:
            hit = True; break
        steps += 1
    if side == 0:
        perp_wall_dist = (map_x - ray_x + (1 - step_x)/2) / (dir_x if dir_x!=0 else 1e-9)
    else:
        perp_wall_dist = (map_y - ray_y + (1 - step_y)/2) / (dir_y if dir_y!=0 else 1e-9)
    hit_x = ray_x + perp_wall_dist * dir_x
    hit_y = ray_y + perp_wall_dist * dir_y
    return perp_wall_dist, side, map_x, map_y, hit_x, hit_y

def draw_floor_ceiling(col_chars, wall_top, wall_bottom, ray_dir_x, ray_dir_y, px, py):
    for y in range(wall_bottom+1, SCREEN_HEIGHT):
        p = y - SCREEN_HEIGHT/2.0
        if p == 0: continue
        row_dist = (SCREEN_HEIGHT/2.0) / p
        fx = px + ray_dir_x * row_dist
        fy = py + ray_dir_y * row_dist
        shade_index = int(min(len(FLOOR_SHADES)-1, max(0, row_dist/6.0 * (len(FLOOR_SHADES)-1))))
        ch = FLOOR_SHADES[shade_index]
        col_chars[y] = ch
    for y in range(0, wall_top):
        col_chars[y] = CEILING_CHAR

# -------------------- ENTITY MOVEMENT / AI --------------------
def can_move_to(nx, ny, radius=PLAYER_RADIUS):
    for dx in (-radius, radius):
        for dy in (-radius, radius):
            cx = nx + dx; cy = ny + dy
            if cx < 0 or cy < 0 or cx >= MAP_W or cy >= MAP_H: return False
            if grid[int(cy)][int(cx)] == 1: return False
    return True

def attempt_move_entity(e, vx, vy):
    nx = e['x'] + vx; ny = e['y']
    if can_move_to(nx, ny, radius=0.18): e['x'] = nx
    else:
        nx = e['x'] + vx*0.5
        if can_move_to(nx, ny, radius=0.18): e['x'] = nx
    nx = e['x']; ny = e['y'] + vy
    if can_move_to(nx, ny, radius=0.18): e['y'] = ny
    else:
        ny = e['y'] + vy*0.5
        if can_move_to(nx, ny, radius=0.18): e['y'] = ny

def update_sprites(dt):
    for s in sprites:
        if s.get('hp',0) <= 0:
            s['alive'] = False
            continue
        if s['last_shot_flash'] > 0:
            s['last_shot_flash'] = max(0, s['last_shot_flash'] - dt)
        if s['melee_cd'] > 0:
            s['melee_cd'] = max(0, s['melee_cd'] - dt)
        dx = player_x - s['x']; dy = player_y - s['y']
        dist = sqrt(dx*dx + dy*dy)
        if s['state'] == 'patrol':
            if dist < s['detect']:
                s['state'] = 'chase'
            else:
                tx, ty = s['patrol'][s['pi']]
                pdx = tx - s['x']; pdy = ty - s['y']; pd = sqrt(pdx*pdx + pdy*pdy)
                if pd < 0.4:
                    s['pi'] = (s['pi'] + 1) % len(s['patrol'])
                else:
                    vx = (pdx/pd) * s['speed'] * dt
                    vy = (pdy/pd) * s['speed'] * dt
                    attempt_move_entity(s, vx, vy)
        elif s['state'] == 'chase':
            if dist > s['detect'] * 1.8:
                s['state'] = 'patrol'
            else:
                if dist > 0.01:
                    vx = (dx/dist) * (s['speed']+0.6) * dt
                    vy = (dy/dist) * (s['speed']+0.6) * dt
                    attempt_move_entity(s, vx, vy)
        # melee attack if close
        if dist <= ENEMY_MELEE_RANGE and s['melee_cd'] <= 0 and s['alive']:
            # damage player
            apply_player_damage(ENEMY_MELEE_DAMAGE)
            s['melee_cd'] = ENEMY_MELEE_COOLDOWN

# -------------------- SHOOTING / BULLETS --------------------
bullets = []  # visual projectiles: {'x','y','dx','dy','life'}
def fire_bullet(px, py, pa):
    global score
    dx = cos(pa); dy = sin(pa)
    bullets.append({'x': px, 'y': py, 'dx': dx, 'dy': dy, 'life': 0.25})
    # raycast for hit
    step = 0.06; d = 0.0
    while d < DEPTH:
        tx = px + dx * d; ty = py + dy * d
        # walls
        if is_wall(int(tx), int(ty)):
            return False, ('wall', (tx, ty))
        # sprites
        for s in sprites:
            if not s['alive']: continue
            if abs(s['x'] - tx) < 0.7 and abs(s['y'] - ty) < 0.7:
                s['hp'] -= PLAYER_SHOT_DAMAGE
                s['last_shot_flash'] = 0.6
                # if hp <=0, mark dead and award score only once
                if s['hp'] <= 0:
                    if not s.get('killed_reported'):
                        s['alive'] = False
                        s['killed_reported'] = True
                        score += 100  # increment score on kill
                return True, ('sprite', s)
        d += step
    return False, None

player_hp = PLAYER_MAX_HP
def apply_player_damage(dmg):
    global player_hp
    player_hp -= dmg
    if player_hp < 0: player_hp = 0

# -------------------- RENDER --------------------
def render_frame(px, py, pa, score, message):
    columns = [' ' * SCREEN_HEIGHT for _ in range(SCREEN_WIDTH)]
    for col in range(SCREEN_WIDTH):
        ray_angle = (pa - FOV/2.0) + (col / SCREEN_WIDTH) * FOV
        rx = cos(ray_angle); ry = sin(ray_angle)
        perp_dist, side, mx, my, hx, hy = cast_single_ray(px, py, rx, ry)
        depth_buffer[col] = 1.0 / perp_dist if perp_dist != 0 else 1e9
        line_h = int(SCREEN_HEIGHT / (perp_dist if perp_dist>0.0001 else 0.0001))
        draw_start = -line_h//2 + SCREEN_HEIGHT//2
        draw_end = line_h//2 + SCREEN_HEIGHT//2
        draw_start = max(0, min(SCREEN_HEIGHT-1, draw_start))
        draw_end = max(0, min(SCREEN_HEIGHT-1, draw_end))
        shade_idx = int(min(len(WALL_SHADES)-1, max(0, (perp_dist / (DEPTH/4.0))*(len(WALL_SHADES)-1))))
        wall_char = WALL_SHADES[shade_idx]
        if side == 1 and shade_idx < len(WALL_SHADES)-1:
            wall_char = WALL_SHADES[min(len(WALL_SHADES)-1, shade_idx+1)]
        col_chars = [CEILING_CHAR] * SCREEN_HEIGHT
        for y in range(draw_start, draw_end+1):
            col_chars[y] = wall_char
        draw_floor_ceiling(col_chars, draw_start, draw_end, rx, ry, px, py)
        columns[col] = ''.join(col_chars)
    # bullets visuals
    for b in list(bullets):
        bx = b['x']; by = b['y']
        dx = bx - px; dy = by - py
        bdist = sqrt(dx*dx + dy*dy)
        if bdist < 0.0001: continue
        bang = atan2(dy, dx) - pa
        while bang < -pi: bang += 2*pi
        while bang > pi: bang -= 2*pi
        if abs(bang) > FOV/2: continue
        scx = int((bang + FOV/2) / FOV * SCREEN_WIDTH)
        if scx < 0 or scx >= SCREEN_WIDTH: continue
        if depth_buffer[scx] > (1.0 / (bdist if bdist>0 else 1e-9)): continue
        try:
            col = list(columns[scx]); col_pos = SCREEN_HEIGHT//2
            col[col_pos] = '*'; columns[scx] = ''.join(col)
        except: pass
    # sprites overlay
    visible = []
    for s in sprites:
        if not s['alive'] and s.get('hp',0) <= 0:
            # render corpse small 'x' at location (optional)
            pass
        dx = s['x'] - px; dy = s['y'] - py
        sd = sqrt(dx*dx + dy*dy)
        if sd < 0.001: continue
        ang = atan2(dy, dx) - pa
        while ang < -pi: ang += 2*pi
        while ang > pi: ang -= 2*pi
        if abs(ang) < FOV/2 + 0.25:
            sx = int((ang + FOV/2) / FOV * SCREEN_WIDTH)
            sh = int(SCREEN_HEIGHT / (sd if sd>0.001 else 0.001) * 0.9)
            visible.append((sd, sx, sh, s))
    visible.sort(key=lambda x: x[0], reverse=True)
    for sd, sx, sh, s in visible:
        half = sh//2; mid = SCREEN_HEIGHT//2; left = sx - half; right = sx + half
        for x in range(left, right+1):
            if x < 0 or x >= SCREEN_WIDTH: continue
            if depth_buffer[x] < (1.0 / sd if sd>0 else 1e9): continue
            try:
                col = list(columns[x])
                top = mid - half; bot = mid + half
                for y in range(top, bot+1):
                    if y < 0 or y >= SCREEN_HEIGHT: continue
                    ch = 'X' if s.get('last_shot_flash',0) > 0 else s['char']
                    # if dead but hp<=0, show corpse 'x'
                    if not s['alive'] and s.get('hp',0) <= 0:
                        ch = 'x'
                    col[y] = ch
                columns[x] = ''.join(col)
            except: pass
    # HUD compose
    rows = []
    hp_bar_len = 30
    hp_ratio = player_hp / PLAYER_MAX_HP
    hp_fill = int(hp_ratio * hp_bar_len)
    hp_bar = '[' + '#' * hp_fill + ' ' * (hp_bar_len - hp_fill) + ']'
    hud = f"HP:{player_hp}/{PLAYER_MAX_HP} {hp_bar}  Score:{score}  Msg:{message}"
    rows.append(hud.ljust(SCREEN_WIDTH)[:SCREEN_WIDTH])
    rows.append(("W/S forward/back  A/D strafe  ←/→ turn  Space shoot  Q quit").ljust(SCREEN_WIDTH)[:SCREEN_WIDTH])
    rows.append("-"*SCREEN_WIDTH)
    for r in range(SCREEN_HEIGHT):
        row_chars = [columns[c][r] for c in range(SCREEN_WIDTH)]
        rows.append(''.join(row_chars))
    return "\n".join(rows)

# -------------------- MAIN LOOP & STATES --------------------
def start_screen():
    clear_screen()
    ascii_wolf3d = [
        " █████╗ ███████╗ ██████╗██╗ ██╗    ██╗    ██╗██████╗ ██████╗ ███████╗          ██████╗ ██████╗  ".center(SCREEN_WIDTH),
        "██╔══██╗██╔════╝██╔════╝██║ ██║    ██║    ██║██╔══██╗██╔══██╗██╔════╝          ╚════██╗██   ██═╗".center(SCREEN_WIDTH),
        "███████║███████╗██║     ██║ ██║    ██║ █╗ ██║██████╔╝██████╔╝███████╗ ███████╗  █████╔╝██    ██║".center(SCREEN_WIDTH),
        "██╔══██║╚════██║██║     ██║ ██║    ██║███╗██║██╔═══╝ ██╔═══╝ ╚════██║ ╚══════╝  ╚═══██╗██   ██╔╝".center(SCREEN_WIDTH),
        "██║  ██║███████║╚██████╗██║ ██║    ╚███╔███╔╝██║     ██║     ███████║          ██████╔╝█████╔═╝ ".center(SCREEN_WIDTH),
        "╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝ ╚═╝     ╚══╝╚══╝ ╚═╝     ╚═╝     ╚══════╝          ╚═════╝ ╚════╝   ".center(SCREEN_WIDTH)
    ]
    lines = [
        "ASCII Raycaster — v3".center(SCREEN_WIDTH),
        "",
        *ascii_wolf3d,
        "",
        "Controls: W/S forward/back  A/D strafe  ←/→ turn  Space shoot  Q quit".center(SCREEN_WIDTH),
        "",
        "Enemies have HP and will attack you when close.".center(SCREEN_WIDTH),
        "",
        "Press any key to START".center(SCREEN_WIDTH)
    ]
    print("\n" * ((SCREEN_HEIGHT//2)-6))
    for l in lines:
        print(l)
    # wait for any key
    while True:
        refresh_key_states()
        if KEY_TIMESTAMP:
            return
        time.sleep(0.03)

def game_over_screen(final_score):
    clear_screen()
    game_over = [
        " ██████╗  █████╗ ███╗   ███╗███████╗     ██████╗ ██╗   ██╗███████╗██████╗ ".center(SCREEN_WIDTH),
        "██╔════╝ ██╔══██╗████╗ ████║██╔════╝    ██╔═══██╗██║   ██║██╔════╝██╔══██╗".center(SCREEN_WIDTH),
        "██║  ███╗███████║██╔████╔██║█████╗      ██║   ██║██║   ██║█████╗  ██████╔╝".center(SCREEN_WIDTH),
        "██║   ██║██╔══██║██║╚██╔╝██║██╔══╝      ██║   ██║██║   ██║██╔══╝  ██╔══██╗".center(SCREEN_WIDTH),
        "╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗    ╚██████╔╝╚██████╔╝███████╗██║  ██║".center(SCREEN_WIDTH),
        " ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝     ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝".center(SCREEN_WIDTH),
    ]
    lines = [
        "GAME OVER".center(SCREEN_WIDTH),
        "",
        *game_over,
        "",
        f"You died. Score: {final_score}".center(SCREEN_WIDTH),
        "",
        "Press R to Restart or Q to Quit".center(SCREEN_WIDTH),
    ]
    print("\n" * ((SCREEN_HEIGHT//2)-4))
    for l in lines:
        print(l)
    # wait for R or Q
    while True:
        refresh_key_states()
        if key_is_down('r') or key_is_down('R'):
            return 'restart'
        if key_is_down('q') or key_is_down('Q'):
            return 'quit'
        time.sleep(0.05)

def winner_screen(winner):
    clear_screen()
    you_win = [
        "██╗   ██╗ ██████╗ ██╗   ██╗    ██╗    ██╗██╗███╗   ██╗".center(SCREEN_WIDTH),
        "╚██╗ ██╔╝██╔═══██╗██║   ██║    ██║    ██║██║████╗  ██║".center(SCREEN_WIDTH),
        " ╚████╔╝ ██║   ██║██║   ██║    ██║ █╗ ██║██║██╔██╗ ██║".center(SCREEN_WIDTH),
        "  ╚██ ╔╝ ██║   ██║██║   ██║    ██║███╗██║██║██║╚██╗██║".center(SCREEN_WIDTH),
        "  ╚██╔╝  ╚██████╔╝╚██████╔╝    ╚███╔███╔╝██║██║ ╚████║".center(SCREEN_WIDTH),
        "   ╚═╝    ╚═════╝  ╚═════╝      ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝".center(SCREEN_WIDTH)
    ]

    lines = [
        "YOU WIN!".center(SCREEN_WIDTH),
        "",
        *you_win,
        "",
        f"Score: {winner}".center(SCREEN_WIDTH),
        "",
        "Press R to Restart or Q to Quit".center(SCREEN_WIDTH),
    ]
    print("\n" * ((SCREEN_HEIGHT//2)-4))
    for l in lines:
        print(l)
    # wait for R or Q
    while True:
        refresh_key_states()
        if key_is_down('r') or key_is_down('R'):
            return 'restart'
        if key_is_down('q') or key_is_down('Q'):
            return 'quit'
        time.sleep(0.05)

def main_loop():
    global game_state, player_x, player_y, player_angle, player_hp, score, bullets, sprites, STOP_INPUT_THREAD
    input_thread = start_input_thread()
    last_time = time.time()
    message = "Welcome"
    try:
        while True:
            if game_state == 'menu':
                start_screen()
                reset_world()
                game_state = 'playing'
                last_time = time.time()
                message = "Fight!"
            elif game_state == 'playing':
                t0 = time.time(); dt = t0 - last_time; last_time = t0
                refresh_key_states()
                forward = key_is_down('w') or key_is_down('up')
                back    = key_is_down('s') or key_is_down('down')
                strafe_l= key_is_down('a')
                strafe_r= key_is_down('d')
                turn_l  = key_is_down('LEFT')
                turn_r  = key_is_down('RIGHT')
                shoot_k = key_is_down(' ') or key_is_down('space') or key_is_down('\r')
                if key_is_down('q') or key_is_down('Q'):
                    break
                if turn_l: player_angle -= TURN_SPEED * dt
                if turn_r: player_angle += TURN_SPEED * dt
                movex = movey = 0.0
                if forward:
                    movex += cos(player_angle) * MOVE_SPEED * dt
                    movey += sin(player_angle) * MOVE_SPEED * dt
                if back:
                    movex -= cos(player_angle) * MOVE_SPEED * dt
                    movey -= sin(player_angle) * MOVE_SPEED * dt
                if strafe_l:
                    movex += cos(player_angle - pi/2) * STRAFE_SPEED * dt
                    movey += sin(player_angle - pi/2) * STRAFE_SPEED * dt
                if strafe_r:
                    movex += cos(player_angle + pi/2) * STRAFE_SPEED * dt
                    movey += sin(player_angle + pi/2) * STRAFE_SPEED * dt
                nx = player_x + movex; ny = player_y
                if can_move_to(nx, ny): player_x = nx
                else:
                    nx = player_x + movex*0.5
                    if can_move_to(nx, ny): player_x = nx
                nx = player_x; ny = player_y + movey
                if can_move_to(nx, ny): player_y = ny
                else:
                    ny = player_y + movey*0.5
                    if can_move_to(nx, ny): player_y = ny
                if shoot_k:
                    now = time.time()
                    if not hasattr(main_loop, 'last_shot') or now - main_loop.last_shot > 0.14:
                        main_loop.last_shot = now
                        hit, res = fire_bullet(player_x, player_y, player_angle)
                        if hit:
                            if res[0] == 'sprite': message = "Hit enemy!"
                        else:
                            message = "Bang!"
                for b in list(bullets):
                    b['life'] -= dt; b['x'] += b['dx'] * 12.0 * dt; b['y'] += b['dy'] * 12.0 * dt
                    if b['life'] <= 0: bullets.remove(b)
                update_sprites(dt)
                # check player death
                if player_hp <= 0:
                    game_state = 'gameover'
                    final_score = score
                    # small pause
                    time.sleep(0.2)
                    continue
                if score == 600:
                    game_state = 'winner'
                    final_score = score
                    # small pause
                    time.sleep(0.2)
                    continue
                frame = render_frame(player_x, player_y, player_angle, score, message)
                clear_screen(); print(frame)
                elapsed = time.time() - t0
                to_sleep = max(0.0, (1.0 / FPS_TARGET) - elapsed)
                time.sleep(to_sleep)
            elif game_state == 'winner':
                res = winner_screen(final_score)
                if res == 'restart':
                    reset_world()
                    game_state = 'playing'
                    last_time = time.time()
                    continue
                else:
                    break
            elif game_state == 'gameover':
                res = game_over_screen(score)
                if res == 'restart':
                    reset_world()
                    game_state = 'playing'
                    last_time = time.time()
                    continue
                else:
                    break
    except KeyboardInterrupt:
        pass
    finally:
        STOP_INPUT_THREAD = True
        time.sleep(0.02)
        if PLATFORM == 'unix':
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except Exception:
                pass
        clear_screen()
        print("Bye!")

if __name__ == '__main__':
    main_loop()
