@echo off
chcp 65001 >nul
title USB文件监控备份系统 - 打包工具
echo ========================================
echo USB文件监控备份系统 - 打包工具
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.6或更高版本
    pause
    exit /b 1
)

REM 检查是否安装了必要的模块
echo [信息] 检查Python环境...
python -c "import sys; print('Python版本:', sys.version)" 2>nul
if errorlevel 1 (
    echo [错误] Python环境异常
    pause
    exit /b 1
)

echo.
echo [信息] 安装依赖包...
pip install psutil pywin32 pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo [警告] 依赖安装失败，尝试继续打包...
)

echo.
echo [信息] 正在打包为EXE文件...
echo 注意：这可能需要几分钟时间，请耐心等待...
echo.

REM 清理之前的打包文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist USBBackup.spec del USBBackup.spec 2>nul

REM 检查图标文件是否存在
if not exist "app.ico" (
    echo [警告] 未找到图标文件 app.ico，将使用默认图标
    set ICON_OPTION=
) else (
    set ICON_OPTION=--icon=app.ico
)

REM 打包为单个EXE文件
pyinstaller --onefile --windowed %ICON_OPTION% --name=USBBackup --clean --noconfirm main.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    echo 可能的原因：
    echo 1. 缺少必要的模块
    echo 2. Python环境问题
    echo 3. 权限不足
    echo.
    echo 请尝试手动安装依赖：pip install psutil pywin32
    echo 然后手动打包：pyinstaller --onefile --windowed --icon=app.ico --name=USBBackup main.py
    pause
    exit /b 1
)

echo.
echo [成功] 打包完成！
echo.
echo 生成的文件：
echo   主程序: dist\USBBackup.exe
echo   配置文件: config.json (首次运行自动生成)
echo   日志目录: logs\
echo   备份目录: USB_Backup\
echo.
echo 使用方法：
echo   1. 首次运行: dist\USBBackup.exe
echo   2. 程序会自动设置开机自启动
echo   3. 程序会在后台静默运行
echo   4. 插入USB会自动备份指定类型的文件
echo.
echo 按任意键打开输出目录并测试程序...
pause >nul

REM 复制配置文件到dist目录（如果存在）
if exist config.json copy config.json dist\ 2>nul

REM 打开目录并测试运行
start "" dist
timeout /t 2 >nul
echo.
echo [信息] 正在测试运行程序（5秒后自动关闭）...
echo 如果看到错误提示，请检查上面的步骤
echo.
start "" /B dist\USBBackup.exe
timeout /t 5 >nul
taskkill /f /im USBBackup.exe 2>nul
echo.
echo [信息] 测试完成！
echo 现在可以正常运行 dist\USBBackup.exe 了
echo.
pause