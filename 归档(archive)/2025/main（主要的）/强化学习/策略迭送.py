import numpy as np

print([(c, 1) for c in range(0, 5)] + [(c, 3) for c in range(1, 6)])
# ---------- 环境 ----------
def get_state(row, col):
    if (row, col) == (0, 0): return 'start'
    if (row, col) == (5, 11): return 'terminal'
    if (row, col) in [(c, 1) for c in range(0, 5)] + [(c, 3) for c in range(1, 6)] + [(1, 5), (3, 5), (5, 5), (4, 7), (4, 9)] + [(c, 6) for c in range(1, 4)] + [(5, r) for r in range(8, 10)] + [(r, 10) for r in range(1,5)] + [(r, 8) for r in range(0, 3)]: return 'trap'
    return 'ground'

def move(row, col, action):
    if get_state(row, col) in ['trap', 'terminal']:
        return row, col, 0
    
    if action == 0: row -= 1    # up
    elif action == 1: row += 1  # down
    elif action == 2: col -= 1  # left
    elif action == 3: col += 1  # right

    row = min(max(row, 0), 5)
    col = min(max(col, 0), 11)

    reward = -1
    if get_state(row, col) == 'trap': reward = -100
    elif get_state(row, col) == 'terminal': reward = 100
    return row, col, reward


# ---------- 值迭代 ----------
ROWS, COLS, ACTIONS = 6, 12, 4
GAMMA = 0.9

values = np.zeros((ROWS, COLS))
policy = np.zeros((ROWS, COLS), dtype=int)  # 初始化策略为随机策略


for _ in range(500):  # 迭代次数
    new_values = np.copy(values)
    for r in range(ROWS):
        for c in range(COLS):
            if get_state(r, c) in ['trap', 'terminal']:
                continue
            q_values = []
            for a in range(ACTIONS):
                nr, nc, reward = move(r, c, a)
                v = 0 if get_state(nr, nc) in ['trap','terminal'] else values[nr, nc]
                q_values.append(reward + GAMMA * v)
            new_values[r, c] = max(q_values)
            policy[r, c] = np.argmax(q_values)
    values = new_values

# ---------- 可视化 ----------
def show_policy(policy):
    symbols = ['↑','↓','←','→']
    for r in range(ROWS):
        line = ''
        for c in range(COLS):
            s = get_state(r, c)
            if s == 'terminal': line += 'G '
            elif s == 'trap': line += 'C '
            elif (r,c) == (0,0): line += 'S '
            else: line += symbols[policy[r,c]] + ' '
        print(line)

print("最终价值函数：")
print(values.round(1))
print("\n最优策略：")
show_policy(policy)
