# Transformer架构（自然语言处理）
尝试学习和从零构建一个大语言模型

![download](https://github.com/user-attachments/assets/467274c7-c2fc-41ae-a62e-eacdb942bbcc)

## 项目简介
这是一个基于Transformer架构的小型文本生成模型，旨在帮助理解和实践Transformer架构的核心概念。本项目从零开始构建，包含了完整的模型训练流程。

## 核心组件
Transformer架构主要包含以下核心组件：

### 编码器(Encoder)
Encoder主要负责将输入转换为计算机能够理解的内容（也就是词表中的向量词元）

### 解码器(Decoder)
将词元的向量内容还原回人类可以理解的内容

### 词表(Tokenizer)
模型所使用的词汇是基于词表中有的词元所生成的，词表可以由大量的文本内容训练，并且训练模式需要符合标准BPE格式

### 训练集(Training set)
大量的现实网络中人们的对话、沟通数据，需要确保数据是干净的

### 训练算法(T5)
通过梯度下降等方法降低模型的损失（令模型回复的内容越来越接近训练集的内容）

## 环境要求
### 硬件配置
- GPU: NVIDIA RTX 3090 24GB或同等性能显卡
- 内存: 建议16GB以上
- 存储: 建议10GB以上可用空间

### 软件环境
- Python: 3.9
- CUDA: 11.8
- 训练时长: 约50分钟（使用RTX 3090）

### 依赖包
- torch >= 2.0.0
- transformers >= 4.46.1
- tokenizers >= 0.21.1
- datasets >= 3.2.0
- peft >= 0.15.2
- trl >= 0.16.1
- numpy >= 1.24.4

## 更新日志
### MiniChat 1.4
- 优化了模型架构，引入了增强型Transformer结构
- 改进了训练参数配置，包括学习率调整和梯度裁剪
- 添加了温度系数和top-k采样等生成参数
- 新增了模型生成脚本generate.py
- 优化了数据处理流程，支持动态截断和padding
- 改进了位置编码实现
- 增强了输出层设计
- 模型结构：
  * 增强型Transformer架构(编码器+解码器)
  * 词嵌入维度(d_model): 256
  * 注意力头数(num_heads): 8
  * 编码器/解码器层数: 4
  * 前馈网络维度: 1024
  * 激活函数: GELU
  * Dropout率: 0.1
- 训练参数：
  * 学习率: 5e-5
  * 批次大小: 32
  * 权重衰减: 0.01
  * 标签平滑: 0.1
  * 梯度裁剪: 1.0
  * 预热步数: 4000
- 生成参数：
  * 温度系数: 0.7
  * Top-k采样: 40

## 快速开始

### 1. 环境配置
1. 确保已安装Python 3.8或更高版本
2. 安装所需依赖：
   ```sh
   pip install -r requirements.txt
   ```
   主要依赖包括：torch、transformers、tokenizers等

### 2. 数据准备
1. 准备训练数据文件：
   - 将文本数据保存为`processed_data.txt`
   - 确保文件编码为UTF-8
   - 放置在项目根目录下
2. 数据格式要求：
   - 每行一个完整的文本段落
   - 确保数据质量，避免特殊字符和乱码

### 3. 训练词表
1. 打开Jupyter Notebook：
   ```sh
   jupyter notebook
   ```
2. 运行`train_BPE_tokenizer.ipynb`文件：
   - 按顺序执行所有单元格
   - 完成后会生成`bpe_tokenizer.json`文件

### 4. 模型训练
1. 运行训练脚本：
   ```sh
   python train.py
   ```
2. 训练过程：
   - 自动加载已准备的数据和词表
   - 显示训练进度和损失值
   - 完成后生成`best_model.pth`

### 5. 文本生成
1. 运行生成脚本：
   ```sh
   python generate.py
   ```
2. 参数调整：
   - 在`generate.py`中修改Config类的参数
   - temperature：控制生成文本的随机性（0.1-1.0）
   - top_k：控制每次生成时考虑的候选词数量

## 项目结构
- `train_BPE_tokenizer.ipynb`: 词表训练脚本
- `train.py`: 模型训练主脚本
- `generate.py`: 文本生成脚本
- `requirements.txt`: 项目依赖文件
- `processed_data.txt`: 训练数据文件
- `best_model.pth`: 训练好的模型文件
- `bpe_tokenizer.json`: 训练好的分词器文件

## 注意事项
- 确保安装了所有必需的依赖包
- 训练数据需要保证质量和清洁度
- 建议使用GPU进行模型训练以提高效率


### 历史版本
---
#### MiniChat 1.0
   - 基于Jupyter Notebook的初始实现
   - 包含基础的BPE分词器训练
   - 实现了简单的Transformer架构
   - 模型结构：
     * 基础Transformer Decoder架构
     * 词嵌入维度(d_model): 64
     * 注意力头数(num_heads): 4
     * 解码器层数(num_layers): 3
     * 前馈网络维度(dim_feedforward): 128
   - 训练参数：
     * 学习率: 0.001
     * 批次大小: 16
     * 使用Adam优化器
     * 使用StepLR学习率调度器

#### MiniChat 1.2
   - 改进了模型训练代码
   - 优化了数据处理流程
   - 添加了模型保存功能
   - 模型结构：沿用1.0版本架构
   - 训练改进：
     * 增加了训练过程可视化
     * 实现了多轮训练模型保存
     * 优化了模型评估模式切换

#### MiniChat 1.3
   - 将Notebook转换为独立Python脚本
   - 优化了训练流程
   - 改进了模型结构
   - 架构优化：
     * 增加了设备自动检测(CPU/GPU)
     * 改进了Transformer的维度处理
     * 优化了位置编码实现
   - 训练改进：
     * 实现了实时损失可视化
     * 增加了训练进度显示





