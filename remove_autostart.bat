@echo off
chcp 65001 >nul
title USB备份系统 - 移除自启动工具
echo ========================================
echo USB文件监控备份系统 - 移除自启动工具
echo ========================================
echo.
echo 本工具将移除USB备份系统的开机自启动
echo 注意：这不会删除程序文件，只是移除自启动
echo.

setlocal enabledelayedexpansion

REM 获取当前用户名
for /f "tokens=2 delims==" %%a in ('wmic OS Get localname /value') do set "PCNAME=%%a"
for /f "tokens=2 delims==" %%a in ('wmic computersystem get username /value ^| findstr /r /v "^$"') do set "CURRENT_USER=%%a"

echo 计算机名: !PCNAME!
echo 当前用户: !CURRENT_USER!
echo.

REM 定义启动文件夹路径
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "STARTUP_FOLDER2=%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"

echo 搜索启动文件夹...
if exist "!STARTUP_FOLDER!" (
    echo 找到启动文件夹: !STARTUP_FOLDER!
    set FOUND=1
) else if exist "!STARTUP_FOLDER2!" (
    echo 找到启动文件夹: !STARTUP_FOLDER2!
    set "STARTUP_FOLDER=!STARTUP_FOLDER2!"
    set FOUND=1
) else (
    echo [错误] 未找到启动文件夹
    set FOUND=0
)

if !FOUND! equ 1 (
    echo.
    echo 正在搜索USB备份系统的自启动文件...
    echo.

    REM 查找相关文件
    set FILE_COUNT=0
    set FILES_FOUND=

    if exist "!STARTUP_FOLDER!\USBBackup.bat" (
        echo 1. !STARTUP_FOLDER!\USBBackup.bat
        set /a FILE_COUNT+=1
        set FILES_FOUND=!FILES_FOUND! "USBBackup.bat"
    )

    if exist "!STARTUP_FOLDER!\USBBackup.lnk" (
        echo 2. !STARTUP_FOLDER!\USBBackup.lnk
        set /a FILE_COUNT+=1
        set FILES_FOUND=!FILES_FOUND! "USBBackup.lnk"
    )

    if exist "!STARTUP_FOLDER!\USB_File_Backup.bat" (
        echo 3. !STARTUP_FOLDER!\USB_File_Backup.bat
        set /a FILE_COUNT+=1
        set FILES_FOUND=!FILES_FOUND! "USB_File_Backup.bat"
    )

    if exist "!STARTUP_FOLDER!\USB_File_Backup.lnk" (
        echo 4. !STARTUP_FOLDER!\USB_File_Backup.lnk
        set /a FILE_COUNT+=1
        set FILES_FOUND=!FILES_FOUND! "USB_File_Backup.lnk"
    )

    REM 查找所有可能的bat文件
    echo.
    echo 正在搜索其他可能的自启动文件...
    for %%f in ("!STARTUP_FOLDER!\*.bat") do (
        findstr /i "USBBackup" "%%f" >nul 2>&1
        if !errorlevel! equ 0 (
            echo 5. %%f
            set /a FILE_COUNT+=1
            set FILES_FOUND=!FILES_FOUND! "%%~nxf"
        )
    )

    echo.
    if !FILE_COUNT! equ 0 (
        echo [信息] 未找到USB备份系统的自启动文件
    ) else (
        echo 共找到 !FILE_COUNT! 个自启动文件
        echo.
        choice /c yn /n /m "是否删除这些文件？(Y/N)"
        if !errorlevel! equ 1 (
            echo.
            echo 正在删除文件...
            for %%f in (!FILES_FOUND!) do (
                del "!STARTUP_FOLDER!\%%~f" 2>nul
                if exist "!STARTUP_FOLDER!\%%~f" (
                    echo [失败] 无法删除: %%~f
                ) else (
                    echo [成功] 已删除: %%~f
                )
            )
            echo.
            echo [完成] 自启动已移除！
        ) else (
            echo.
            echo [信息] 已取消操作
        )
    )
)

echo.
echo ========================================
echo 其他移除方法：
echo 1. 手动打开启动文件夹：按 Win+R，输入 shell:startup
echo 2. 删除所有与USB备份相关的文件
echo 3. 或者运行程序时选择禁用自启动
echo ========================================
echo.
pause