@echo off
chcp 65001 >nul
title USB备份系统 - 完全卸载工具
echo ========================================
echo USB文件备份系统 - 完全卸载工具
echo ========================================
echo.
echo 警告：这将完全卸载USB备份系统，包括：
echo   1. 移除开机自启动
echo   2. 停止运行中的程序
echo   3. 删除备份文件和配置文件
echo   4. 删除日志文件
echo.
echo 请确保已备份重要数据！
echo.

choice /c yn /n /m "确定要继续吗？(Y/N)"
if errorlevel 2 (
    echo.
    echo [信息] 已取消卸载
    pause
    exit /b 0
)

echo.
echo [步骤1/5] 停止运行中的程序...
taskkill /f /im USBBackup.exe 2>nul
taskkill /f /im python.exe 2>nul
timeout /t 2 >nul
echo [完成] 程序已停止

echo.
echo [步骤2/5] 移除开机自启动...
call remove_autostart.bat
echo [完成] 自启动已移除

echo.
echo [步骤3/5] 删除程序文件...
if exist dist\USBBackup.exe (
    del dist\USBBackup.exe 2>nul
    echo [完成] 删除程序文件
) else (
    echo [信息] 未找到程序文件
)

echo.
echo [步骤4/5] 删除数据文件...
set CONFIRM_DELETE=0
if exist USB_Backup\ (
    echo 发现备份文件夹: USB_Backup\
    choice /c yn /n /m "是否删除备份文件？(Y/N)"
    if errorlevel 1 (
        rmdir /s /q USB_Backup 2>nul
        echo [完成] 删除备份文件
        set CONFIRM_DELETE=1
    )
)

if exist logs\ (
    if %CONFIRM_DELETE% equ 1 (
        rmdir /s /q logs 2>nul
        echo [完成] 删除日志文件
    )
)

echo.
echo [步骤5/5] 删除配置文件...
del config.json 2>nul
del autostart_config.json 2>nul
del USBBackup.spec 2>nul
echo [完成] 删除配置文件

echo.
echo ========================================
echo 卸载完成！
echo.
echo 已移除的项目：
echo   ✓ 开机自启动
echo   ✓ 程序文件
if %CONFIRM_DELETE% equ 1 (
    echo   ✓ 备份文件
    echo   ✓ 日志文件
)
echo   ✓ 配置文件
echo.
echo 注意：如果需要重新安装，请重新运行 build.bat
echo ========================================
echo.
pause