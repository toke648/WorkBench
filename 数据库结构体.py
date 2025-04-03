from graphviz import Digraph

# 创建一个有向图
dot = Digraph(comment='宠物商店结构图')

# 添加节点和边
dot.node('A', '宠物商店')
dot.node('B', '经理')
dot.node('C', '助理经理')
dot.node('D', '销售员')
dot.node('E', '宠物护理员')
dot.node('F', '清洁工')

# 添加工资信息
dot.node('G', '工资信息')
dot.node('H', '经理: $5000/月')
dot.node('I', '助理经理: $4000/月')
dot.node('J', '销售员: $3000/月')
dot.node('K', '宠物护理员: $3500/月')
dot.node('L', '清洁工: $2500/月')

# 添加工时信息
dot.node('M', '工时信息')
dot.node('N', '经理: 40小时/周')
dot.node('O', '助理经理: 40小时/周')
dot.node('P', '销售员: 35小时/周')
dot.node('Q', '宠物护理员: 30小时/周')
dot.node('R', '清洁工: 20小时/周')

# 添加边
dot.edges(['AB', 'AC', 'AD', 'AE', 'AF'])
dot.edges(['GH', 'GI', 'GJ', 'GK', 'GL'])
dot.edges(['MN', 'MO', 'MP', 'MQ', 'MR'])

# 保存并渲染图形
dot.render('pet_store_structure', format='png', cleanup=True)

# 打印图形
print(dot.source)