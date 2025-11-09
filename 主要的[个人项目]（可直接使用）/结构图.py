from graphviz import Digraph

# 创建有向图
dot = Digraph(comment='政策咨询智能体系统架构', format='png')
dot.attr(rankdir='TB', size='12,8', dpi='300')

# 设置全局样式
dot.attr('node', shape='rectangle', style='rounded,filled', 
         fillcolor='lightblue', fontname='Microsoft YaHei')
dot.attr('edge', fontname='Microsoft YaHei')

# 用户交互层
with dot.subgraph(name='cluster_ui') as ui:
    ui.attr(label='用户交互层', style='filled', fillcolor='lightgrey',
           fontsize='16', fontname='Microsoft YaHei')
    
    ui.node('web_ui', 'Gradio Web界面\n• ChatGPT风格交互\n• 实时对话显示\n• 触摸友好的引用展示',
           shape='rectangle', style='rounded,filled', fillcolor='#E8F4FD')
    
    ui.node('dialog_manager', '对话管理器\n• 多轮对话维护\n• 会话状态管理\n• 上下文记忆',
           shape='rectangle', style='rounded,filled', fillcolor='#E8F4FD')

# 业务逻辑层
with dot.subgraph(name='cluster_business') as business:
    business.attr(label='业务逻辑层', style='filled', fillcolor='lightyellow',
                 fontsize='16', fontname='Microsoft YaHei')
    
    # 意图识别模块
    business.node('intent_engine', '意图识别引擎\n• 8类意图分类\n• 语义分析\n• 关键词提取',
                 shape='rectangle', style='rounded,filled', fillcolor='#FFF2CC')
    
    # 政策检索模块
    business.node('retrieval_engine', '政策检索引擎\n• 知识库检索\n• 联网搜索\n• 相关性评分',
                 shape='rectangle', style='rounded,filled', fillcolor='#FFF2CC')
    
    # 回答生成模块
    business.node('response_engine', '回答生成引擎\n• LLM集成\n• 流式输出\n• 引用标注',
                 shape='rectangle', style='rounded,filled', fillcolor='#FFF2CC')

# 数据服务层
with dot.subgraph(name='cluster_data') as data:
    data.attr(label='数据服务层', style='filled', fillcolor='lightgreen',
             fontsize='16', fontname='Microsoft YaHei')
    
    data.node('knowledge_base', '知识库管理\n• 政策存储\n• 向量检索\n• 版本控制',
             shape='rectangle', style='rounded,filled', fillcolor='#D5E8D4')
    
    data.node('document_parser', '文档解析引擎\n• PDF解析\n• DOCX解析\n• TXT解析',
             shape='rectangle', style='rounded,filled', fillcolor='#D5E8D4')
    
    data.node('crawler_service', '爬虫服务\n• 网页抓取\n• 数据清洗\n• 自动更新',
             shape='rectangle', style='rounded,filled', fillcolor='#D5E8D4')
    
    data.node('database_manager', '数据库管理\n• MySQL/内存双模\n• 自动故障转移\n• 数据持久化',
             shape='rectangle', style='rounded,filled', fillcolor='#D5E8D4')

# 配置模块（独立）
dot.node('config_manager', '配置管理\n• 模型配置\n• 数据库配置\n• 搜索配置\n• UI设置',
        shape='rectangle', style='rounded,filled', fillcolor='#F8CECC')

# 定义数据流关系
# 用户交互层内部关系
dot.edge('web_ui', 'dialog_manager', label='用户输入')

# 用户交互层 → 业务逻辑层
dot.edge('dialog_manager', 'intent_engine', label='解析查询')
dot.edge('intent_engine', 'retrieval_engine', label='意图结果')
dot.edge('retrieval_engine', 'response_engine', label='检索结果')

# 业务逻辑层 → 数据服务层
dot.edge('retrieval_engine', 'knowledge_base', label='知识查询', style='dashed')
dot.edge('retrieval_engine', 'crawler_service', label='联网搜索', style='dashed')
dot.edge('response_engine', 'database_manager', label='历史存储', style='dashed')

# 数据服务层内部关系
dot.edge('document_parser', 'knowledge_base', label='文档导入')
dot.edge('crawler_service', 'knowledge_base', label='数据入库')
dot.edge('knowledge_base', 'database_manager', label='数据持久化')

# 配置模块关系
dot.edge('config_manager', 'intent_engine', label='模型配置', style='dotted')
dot.edge('config_manager', 'response_engine', label='LLM配置', style='dotted')
dot.edge('config_manager', 'database_manager', label='数据库配置', style='dotted')

# 返回结果流
dot.edge('response_engine', 'dialog_manager', label='生成回答', color='red')
dot.edge('dialog_manager', 'web_ui', label='展示结果', color='red')

# 添加图例
with dot.subgraph(name='cluster_legend') as legend:
    legend.attr(label='图例', style='filled', fillcolor='white',
               fontsize='12', fontname='Microsoft YaHei')
    
    legend.node('solid_line', '实线: 主要数据流', 
               shape='plaintext', style='solid', fillcolor='none')
    legend.node('dashed_line', '虚线: 数据查询', 
               shape='plaintext', style='dashed', fillcolor='none')
    legend.node('dotted_line', '点线: 配置依赖', 
               shape='plaintext', style='dotted', fillcolor='none')
    legend.node('red_line', '红色: 结果返回', 
               shape='plaintext', style='solid', fillcolor='none', color='red')

# 生成图片
dot.render('system_architecture', view=True, cleanup=True)

print("系统架构图已生成: system_architecture.png")