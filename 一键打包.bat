@echo off
chcp 65001 > nul
title copy-cat 打包工具
echo.
echo ========================================
echo   copy-cat 一键打包工具
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python
    echo 请先安装Python 3.6+
    pause
    exit /b 1
)

echo 正在检查图标文件...
echo.

REM 检查自定义图标
if exist "copy-cat.ico" (
    echo ✓ 发现自定义图标: copy-cat.ico
) else if exist "icon.ico" (
    echo ✓ 发现图标: icon.ico
    copy "icon.ico" "copy-cat.ico" >nul
    echo   已复制为 copy-cat.ico
) else if exist "custom.ico" (
    echo ✓ 发现图标: custom.ico
    copy "custom.ico" "copy-cat.ico" >nul
    echo   已复制为 copy-cat.ico
) else (
    echo ℹ 未发现自定义图标文件
    echo   将创建默认图标或打包时不使用图标
    echo.
    echo 支持的图标文件名:
    echo   - copy-cat.ico (推荐)
    echo   - icon.ico
    echo   - custom.ico
    echo.
)

echo.
echo 正在启动打包工具...
echo.

REM 运行打包脚本
python build_copy_cat.py

echo.
pause