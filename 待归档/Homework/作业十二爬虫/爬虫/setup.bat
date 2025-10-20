@echo off
echo ===== 初始化开始 =====

REM 激活虚拟环境（如果你在虚拟环境中运行，请取消注释下面这行）
REM call venv\Scripts\activate

REM 安装依赖
if exist requirements.txt (
    echo 正在安装 requirements.txt 中的依赖...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 依赖安装失败，请检查 requirements.txt
        pause
        exit /b
    )
) else (
    echo 未找到 requirements.txt 文件，跳过依赖安装
)

REM 运行第一个脚本
echo 正在运行 homework.py ...
python homework.py
if %errorlevel% neq 0 (
    echo 运行 homework.py 失败
    pause
    exit /b
)

REM 运行第二个脚本
echo 正在运行 J2401008.py ...
python J2401008.py
if %errorlevel% neq 0 (
    echo 运行 J2401008.py 失败
    pause
    exit /b
)

echo ===== 所有任务完成 =====
pause
