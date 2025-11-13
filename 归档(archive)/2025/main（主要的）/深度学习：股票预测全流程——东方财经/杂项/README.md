人工智能学习资料（个人整理）


### 先导
开始之前，让我们先看几个demo和视频

[Training AI to Play Pokemon with Reinforcement Learning
](https://www.youtube.com/watch?v=DcYLT37ImBY&list=PLOjl8vG0-0cusp-vLp-ZNoD9AggghRiYN)



### 路线
书籍资源—理论概念—项目实践——思考记录——拓展

### 学习路径
python基础——人工智能导论——数据分析&数据处理——sklearn实战——pytorch——机器学习——深度学习——强化学习

其中所涉及的有

Python 基础
语法、数据结构、函数、类
Vscode、Anaconda、Jupyter、Numpy、Pandas、Matplotlib

人工智能导论
历史简述：图灵测试、达特茅斯会议、符号主义 vs 连接主义
AI 分类：分类问题、预测问题、策略问题
基础算法：逻辑回归、线性回归、梯度下降

数据分析 & 数据处理
数据标准化、归一化
矩阵运算、特征提取、特征选择
超参数设置与调优

机器学习基础（sklearn 实战）
训练集、验证集、测试集
拟合、过拟合、欠拟合
评估指标：准确率、召回率、F1 分数
损失函数：均方误差、交叉熵损失

深度学习（PyTorch）
神经网络基础：输入层、隐藏层、输出层、权重、偏置、学习率
神经元、激活函数（Sigmoid、ReLU、Softmax）
前向传播、反向传播、梯度下降
优化器：SGD、Adam



深度学习进阶
CNN 卷积神经网络
RNN / LSTM / GRU：序列建模
Transerformer 架构的原理及实现（注意力机制，编码器，解码器，BERT/GPT）
实战：手写数字识别（MNIST）、初学者优先先拿完整的预训练项目直接训练来理解、房价预测、自主构建、SimpleCNN、SimpleRNN、MiniChat



强化学习入门
环境、状态、动作、奖励
Q-learning、DQN、策略梯度




以及算法计算过程和项目代码实战其中都有所包含


### 资料

https://www.runoob.com/
菜鸟教程—— AI & 数据分析
Python、Pytorch、Ollama


### 拓展
拓展：Ollama、Ollama Factory、Yolov5、GPT-SoVITS、Stable Diffusion、魔塔社区（https://www.modelscope.cn/）、Huggenface（https://huggingface.co/）、OpenWebUI（https://docs.openwebui.com/）、小智机器人 & MCP的实现 等等


之后可以根据自己的兴趣做一些感兴趣的东西
我举几个例子：
Ollama Factory微调后部署到群QQai助手（可以调成任何你想要的效果 小春警觉）
结合小智AI&MCP实现的语音交互控制的无人机
与开放世界游戏相结合实现虚拟人物对话（进阶的化通过MCP实现自主任务系统）
类J.A.R.V.I.S. 助手的虚拟人物效果（需要结合MCP协议以及控制终端的功能，我做过类似的：https://github.com/toke648/AI-Interactive-LLM-VTuber）
通过将神经网络模型的芯片连接到小鼠大脑，然后基于小鼠大脑的电信号数据进行直接的模糊性训练（研究脑神经和意识之间的关系）

AI 助手类：
Ollama + MCP → QQ 群 AI 助手 / 桌面助手 / J.A.R.V.I.S 风格
交互类：
无人机控制、机器人语音交互、游戏 NPC 智能化
创作类：
Stable Diffusion / GPT-SoVITS 结合，生成声音和图像内容，打造虚拟人物
研究类：
Transformer 从零实现（你之前的目标），对训练流程、推理代码、数据预处理有深刻理解


这之类的还有很多，总之现在的AI日新月异，高级的理论知识我也不太搞得懂，但我依旧想要提出自己的观点——生成式认知主体

---
### 参考资料

- [1] GoAI（CSDN 博客） [深度学习知识点全面总结
](https://blog.csdn.net/qq_36816848/article/details/122286610?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522d338d39e7f738d8daf90500c90fee987%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=d338d39e7f738d8daf90500c90fee987&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-122286610-null-null.142^v102^pc_search_result_base1&utm_term=%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0&spm=1018.2226.3001.4187)

- [2] 周北, Python深度学习与项目实战, 人民邮电出版社, 2021

- [3] [美]伊恩·古德费洛,[加]约书亚·本吉奥,[加]亚伦·库维尔，深度学习，人民邮电出版社，2021

- [4] [PyTorch深度学习快速入门教程（绝对通俗易懂！）【小土堆】
](https://www.bilibili.com/video/BV1hE411t7RN/?spm_id_from=333.788.player.switch&vd_source=d5f2b87dc23c8806dfc6d9550f24aaf2&p=7)

- [5] [【比刷剧还爽！】一口气学完糖尿病回归预测、鸢尾花大作战、新闻文本分类、手写数字识别等七大机器学习项目实战！（附数据集源码）
](https://www.bilibili.com/video/BV1dM4m1y7KY/?spm_id_from=333.788.videopod.episodes&vd_source=d5f2b87dc23c8806dfc6d9550f24aaf2&p=4)

- [6] [强化学习 简明教程 代码实战
](https://www.bilibili.com/video/BV1Ge4y1i7L6/?spm_id_from=333.788.player.switch&vd_source=d5f2b87dc23c8806dfc6d9550f24aaf2&p=12)

- [7] [【機器學習2021】預測本頻道觀看人數 (上) - 機器學習基本概念簡介
](https://www.youtube.com/watch?v=Ye018rCVvOo&list=PLJV_el3uVTsMhtt7_Y6sgTHGHp1Vb2P2J)

- [8] Attention Is All You Need, https://arxiv.org/pdf/1706.03762
以及解读：
[《Attention is all you need》论文解读及Transformer架构详细介绍
](https://www.bilibili.com/video/BV1xoJwzDESD/?spm_id_from=333.337.search-card.all.click&vd_source=d5f2b87dc23c8806dfc6d9550f24aaf2)
《Attention is all you need》通俗解读，彻底理解版：part1
https://juejin.cn/post/7387690498003812402

- [9] 动手学强化学习
https://hrl.boyuai.com/chapter/1/%E5%88%9D%E6%8E%A2%E5%BC%BA%E5%8C%96%E5%AD%A6%E4%B9%A0/

- [10] 《动手学深度学习》https://zh.d2l.ai/chapter_preliminaries/index.html

- [11] PyTorch 教程 https://www.runoob.com/pytorch/pytorch-tutorial.html

- [12] 機器學習 | [【機器學習2021】預測本頻道觀看人數 (上) - 機器學習基本概念簡介](https://www.youtube.com/watch?v=Ye018rCVvOo&list=PLJV_el3uVTsMhtt7_Y6sgTHGHp1Vb2P2J)