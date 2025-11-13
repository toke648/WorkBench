## 主要的[个人项目]（可直接使用）

本目录收录了可直接运行的个人实践项目与脚本，覆盖爬虫、深度学习、前后端交互、图像处理、强化学习、语音合成、情感分析等。本文档提供环境准备、通用使用步骤、各子项目与常用脚本的功能概览及运行示例，便于快速上手与复用。

### 环境要求
- Python 版本: 建议 3.9 ~ 3.11（Windows 10/11）
- 推荐工具: PowerShell、VSCode、Conda/venv
- 依赖安装: 根目录提供 `requirements.txt`（如部分子项目需要额外依赖，均在对应章节另行说明）

### 快速开始
1) 创建虚拟环境（二选一）
```powershell
# venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 或 Conda（若已安装）
conda create -n workbench python=3.10 -y
conda activate workbench
```

2) 安装通用依赖
```powershell
pip install -r ..\requirements.txt
```

3) 运行示例脚本（以图片批量缩放为例）
```powershell
cd "图片大小批量转换"
python .\main.py
```

4) 如需运行 Web/Notebook/特定模型项目，请参考下方“子项目运行指南”。

---

### 目录结构（摘录）
- `Crawler（爬虫）/`：多类爬虫项目（登录、Pixiv、Scrapy、小说、漫画等）
- `data/`：示例数据、模型权重与实用脚本（如 ChatGPT 输出转 MD、二维码、词频字典等）
- `前后端交互/`：Flask/JS 练习、简单页面与接口示例、图书馆管理系统样例
- `卷积神经网络数字识别/`：CNN 数字识别（含 `cnn_digit_model.pth`、训练/测试脚本）
- `强化学习/`：DynaQ、冰湖、策略迭代、贪婪等 RL 示例
- `情感分析/`：情感分析脚本与样例数据
- `生命游戏/`：细胞自动机相关实现与模型
- `深度学习：股票预测全流程——东方财经/`：数据与 Notebook 工作流
- 其他常用脚本：`PDF文件转换合并.py`、`图片转换为pdf文件.py`、`ico转换器.py`、`wifi_scanner.py`、`二维码生成器.py`、`词云.py`、`豆包API.py` 等

---

### 常见脚本与用途速览
- 图片/文档处理
  - `图片大小批量转换/main.py`：批量读取 `imgs/` 并按统一规格输出至 `output_images/`
  - `图片转换为pdf文件.py`：将多张图片合并为单个 PDF
  - `PDF文件转换合并.py`：对多个 PDF 进行拆分/合并（按脚本提示）
  - `ico转换器.py`：图片转 ICO 图标

- 爬虫与自动化
  - `Crawler（爬虫）/cookie的爬取&登录/`：验证码登录、Cookie 持久化演示
  - `Crawler（爬虫）/Pixiv爬虫/` 与 `Pixiv动态爬虫实现.py`：Pixiv 相关数据抓取
  - `Crawler（爬虫）/Scrapy山东工程/`：Scrapy 配置与示例 spider
  - `图像识别+爬虫自动登录.py`：利用图像识别辅助登录流程

- 机器学习/深度学习
  - `卷积神经网络数字识别/`：CNN 数字分类训练与推理（见下方子项目指南）
  - `强化学习/` 目录：DynaQ、冰湖（FrozenLake）、策略迭代等经典 RL 算法练习
  - `线性回归.py`、`softmax逻辑原理.ipynb`：基础算法实现与原理练习
  - `生命游戏/`：细胞自动机/学习型模型演示
  - `深度学习：股票预测全流程——东方财经/`：含数据、Notebook、流程示例

- NLP / 语音
  - `情感分析/app.py` 与 `外网数据情感分析模型实现.ipynb`：情感分析流程
  - `Gpt-Sovits使用Api生成.py`、`火山引擎-语音合成（tts）.py`：TTS/语音合成调用示例
  - `引用huggenface模型下载并本地文本生成.py`：从 Hugging Face 下载并本地推理示例
  - `豆包API.py`：调用相关大模型/开放平台接口示例

- 实用工具
  - `wifi_scanner.py`：Wi-Fi 网络扫描
  - `二维码生成器.py`：生成二维码（示例输入见 `data/`）
  - `词云.py`：根据文本生成词云
  - `随机图片生成.py`：简单随机图像生成

---

### 子项目运行指南（重点）

#### 1) 图片大小批量转换
目录：`图片大小批量转换/`
```powershell
cd "图片大小批量转换"
pip install -r ..\..\requirements.txt
python .\main.py
```
说明：将 `imgs/` 目录下图片批量缩放并输出到 `output_images/`。

#### 2) 卷积神经网络数字识别（CNN）
目录：`卷积神经网络数字识别/`
```powershell
cd "卷积神经网络数字识别"
pip install -r ..\..\requirements.txt
# 推理（示例）
python .\main.py
# 训练/测试（如需）
python .\杂项\train.py
python .\杂项\test.py
```
说明：提供 `cnn_digit_model.pth` 预训练权重与少量 `train_images/` 示例，可直接运行推理或复现训练流程。

#### 3) 强化学习练习
目录：`强化学习/`
```powershell
cd "强化学习"
pip install -r ..\..\requirements.txt
python .\DynaQ算法.py
python .\冰湖.py
python .\策略迭送.py
```
说明：涵盖 DynaQ、FrozenLake、策略迭代、贪婪策略等经典算法的最小可运行脚本。

#### 4) 情感分析
目录：`情感分析/`
```powershell
cd "情感分析"
pip install -r ..\..\requirements.txt
python .\app.py  # 如为 Web 服务，请根据启动日志访问本地端口
```
说明：包含 `comments.txt` 示例与 Notebook 演示流程。若使用第三方模型，请提前配置代理/下载缓存。

#### 5) 前后端交互（Flask 与 JS）
目录：`前后端交互/`
```powershell
cd "前后端交互\Flask"
pip install -r ..\..\..\requirements.txt
python .\app.py  # 或 python .\server.py

cd "..\图书馆管理系统"
python .\app.py
```
说明：演示 Flask 模板渲染、静态资源与简单 API；图书馆管理系统为极简 CRUD 示例。

#### 6) 爬虫集合
目录：`Crawler（爬虫）/`
```powershell
cd "Crawler（爬虫）\cookie的爬取&登录"
python .\main.py

cd "..\Pixiv爬虫"
python .\s.py

cd "..\Scrapy山东工程"
pip install scrapy
scrapy list
```
说明：不同子目录演示验证码识别、会话持久化、站点结构化抓取与 Scrapy 项目结构等。

---

### 数据与模型
- `data/` 提供示例数据与权重文件，如 `model.pth`、`train.jsonl`、`username-CN-top500.txt` 等
- 运行涉及大文件/外部模型的脚本前，请确认路径与平台访问权限（如 Hugging Face、火山引擎）
- GPU 相关脚本会自动回退 CPU（若未检测到 CUDA），运行速度可能受影响

### 常见问题（FAQ）
- 依赖冲突/缺失：优先使用虚拟环境；按报错信息 `pip install <package>` 补充
- 中文路径/空格：Windows 下建议使用引号包裹路径，例如 `cd "主要的[个人项目]（可直接使用）"`
- 权限/网络：爬虫与模型下载可能受网络限制，必要时配置代理
- 编码问题：若出现 `UnicodeEncodeError`，请将终端切换为 UTF-8 或在代码中显式声明编码

### 维护与约定
- 新增脚本：放入对应主题目录，并在本文档的相应章节补充一句话描述与运行示例
- 大型子项目：建议在子目录内建立独立 `README.md`，说明环境、数据、模型与端口
- 命名规范：脚本名以功能为主、目录名以主题分类；避免过深层级

---

如需我为某个具体脚本/子项目补充更详细的 README 与参数说明，请在消息中指出文件或目录名。


