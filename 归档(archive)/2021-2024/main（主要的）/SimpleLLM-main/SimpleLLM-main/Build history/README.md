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
本项目依赖以下主要Python包：
- torch >= 2.0.0
- transformers >= 4.46.1
- tokenizers >= 0.21.1
- datasets >= 3.2.0
- peft >= 0.15.2
- trl >= 0.16.1
- numpy >= 1.24.4

## 快速开始

1. 准备环境：
   ```sh
   pip install -r requirements.txt
   ```

2. 准备数据：
   - 词元训练集文件：processed_data.txt
   - 确保数据文件放置在项目根目录

3. 训练词表：
   - 打开并运行 [train_BPE_tokenizer.ipynb](train_BPE_tokenizer.ipynb) 文件
   - 按照notebook中的步骤顺序执行

4. 训练模型：
   - 打开并运行 [BPE_Transformer.ipynb](BPE_Transformer.ipynb) 文件
   - 按照notebook中的步骤执行训练流程

## 项目结构
- `train_tokenizer.ipynb`: 词表训练脚本
- `BPE_Transformer.ipynb`: 模型训练主脚本
- `requirements.txt`: 项目依赖文件
- `processed_data.txt`: 训练数据文件

## 注意事项
- 确保安装了所有必需的依赖包
- 训练数据需要保证质量和清洁度
- 建议使用GPU进行模型训练以提高效率





