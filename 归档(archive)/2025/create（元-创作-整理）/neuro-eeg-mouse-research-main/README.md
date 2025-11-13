# 脑神经科学与小鼠电信号研究（neuro-eeg-mouse-research）

- 想法的起点：
[个人自传](https://github.com/toke648/personal-chronicle/blob/main/meta/mainline.md)

⚠️ **伦理与合规提示**  
本仓库仅用于文献收集、模拟与算法研究。任何真实动物实验必须遵守所在机构伦理委员会（IACUC）或等效机构的审批流程，本仓库不包含可直接用于绕开伦理的内容。

## 目标
收集公开数据集、论文、算法与模拟代码，探索“用神经信号训练神经网络以模拟或替代局部脑环路”的可行路径。首阶段重点为数据预处理、特征工程与环路建模（模拟）。

## 目录建议
- 00-README.md
- 01-ethics.md  # 伦理、数据使用、合规说明
- 02-datasets/  # 公开 EEG / LFP / spike datasets references & download scripts
- 03-preprocessing/  # 滤波、伪迹去除、伪标签方法
- 04-models/  # 1D-CNN, RNN, temporal-conv, SNN (spiking neural networks) notes
- 05-simulations/  # 小型环路仿真（Brian2 / NEST 示例）
- 06-papers/

## 贡献
暂无

首批 issues：

- 收集 5 个公开脑电/局部场电位（LFP）数据集链接并写下载脚本

- 写一篇 ethics.md（包含数据使用与动物实验的合规草案）