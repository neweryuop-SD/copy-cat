@echo off
echo ========================================
echo USB文件监控备份系统 - 打包工具
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查依赖
echo [信息] 安装依赖...
pip install -r requirements.txt

echo.
echo [信息] 正在打包为EXE文件...
echo.

REM 打包为单个EXE文件，使用指定的图标
pyinstaller --onefile --windowed --icon=app.ico --name=USBBackup main.py

if errorlevel 1 (
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo [信息] 打包成功！
echo.
echo 生成的EXE文件在: dist\USBBackup.exe
echo.
echo 使用方法:
echo   1. 直接运行: dist\USBBackup.exe
echo   2. 首次运行会自动设置开机自启动
echo   3. 程序会隐藏在后台运行
echo   4. 插入USB设备会自动备份文件
echo.
echo 按任意键打开输出目录...
pause
start dist