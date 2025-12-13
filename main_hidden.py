#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
copy-cat - 后台隐藏版本
无窗口运行，适合作为后台服务
"""

import sys
import os
import time
import traceback
from datetime import datetime

# 隐藏控制台窗口（仅限Windows）
if sys.platform == "win32":
    import ctypes

    # 隐藏控制台窗口
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


def setup_logging():
    """设置日志系统（用于后台运行）"""
    import logging

    # 创建logger
    logger = logging.getLogger('CopyCat')
    logger.setLevel(logging.INFO)

    # 文件handler
    file_handler = logging.FileHandler('copy_cat_service.log', encoding='utf-8')

    # 控制台handler（但不显示，以防万一）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)  # 只记录错误

    # 格式
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 添加handler
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def check_and_install_deps():
    """检查并安装依赖"""
    try:
        import psutil
        import win32api
        return True
    except ImportError:
        # 记录到文件而不是控制台
        with open('install.log', 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now()}: 缺少依赖，请运行: pip install psutil pywin32\n")
        return False


def write_status(message):
    """写入状态信息"""
    try:
        with open('copy_cat_status.log', 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now()}: {message}\n")
    except:
        pass


def main():
    """主函数 - 后台版本"""
    # 写入启动状态
    write_status("copy-cat服务启动")

    # 检查依赖
    if not check_and_install_deps():
        write_status("依赖检查失败")
        return

    try:
        # 导入模块
        from config import Config
        from logger import Logger
        from file_handler import FileHandler
        from monitor import USBMoniTor

        # 初始化配置
        config = Config()

        # 初始化日志
        logger = Logger(config)
        logger.log_info("copy-cat服务启动 (后台模式)")

        # 初始化文件处理器
        file_handler = FileHandler(config, logger)

        # 初始化监控器
        monitor = USBMoniTor(config, logger, file_handler)

        # 写入启动完成状态
        write_status("监控服务运行中...")

        # 开始监控
        monitor.start_monitoring()

    except KeyboardInterrupt:
        write_status("服务被用户中断")
    except Exception as e:
        error_msg = f"服务运行错误: {str(e)}"
        write_status(error_msg)

        # 记录详细错误
        with open('service_error.log', 'a', encoding='utf-8') as f:
            f.write(f"\n{'=' * 50}\n")
            f.write(f"错误时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"错误信息: {str(e)}\n")
            traceback.print_exc(file=f)


def install_service():
    """安装为服务/启动项"""
    write_status("正在安装启动项...")

    try:
        import winreg
        import os

        # 获取当前脚本路径
        if getattr(sys, 'frozen', False):
            # 如果是打包的exe
            exe_path = sys.executable
        else:
            # 如果是Python脚本
            pythonw_path = sys.executable.replace('python.exe', 'pythonw.exe')
            script_path = os.path.abspath(__file__)
            exe_path = f'"{pythonw_path}" "{script_path}"'

        # 添加到注册表启动项（当前用户，不需要管理员权限）
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "copy-cat", 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)

            write_status(f"启动项安装成功: {exe_path}")

            # 创建启动成功标志文件
            with open('installed.flag', 'w', encoding='utf-8') as f:
                f.write(f"安装时间: {datetime.now()}\n")
                f.write(f"启动路径: {exe_path}\n")

            return True
        except Exception as e:
            write_status(f"注册表安装失败: {str(e)}")

            # 备用方法：创建启动文件夹快捷方式
            try:
                startup_folder = os.path.join(
                    os.path.expanduser('~'),
                    'AppData',
                    'Roaming',
                    'Microsoft',
                    'Windows',
                    'Start Menu',
                    'Programs',
                    'Startup'
                )

                # 创建快捷方式
                shortcut_path = os.path.join(startup_folder, "copy-cat.lnk")

                # 使用wscript创建快捷方式
                vbs_content = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{exe_path}"
oLink.Save
"""

                vbs_file = "create_shortcut.vbs"
                with open(vbs_file, 'w', encoding='utf-8') as f:
                    f.write(vbs_content)

                import subprocess
                subprocess.run(['cscript', vbs_file], capture_output=True)
                os.remove(vbs_file)

                write_status(f"启动文件夹快捷方式创建成功: {shortcut_path}")
                return True
            except Exception as e2:
                write_status(f"所有安装方法都失败: {str(e2)}")
                return False

    except Exception as e:
        write_status(f"安装过程出错: {str(e)}")
        return False


def uninstall_service():
    """卸载服务/启动项"""
    write_status("正在卸载启动项...")

    try:
        import winreg

        # 从注册表移除
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "copy-cat")
            winreg.CloseKey(key)
            write_status("注册表启动项已移除")
        except:
            write_status("注册表中未找到启动项")

        # 删除启动文件夹快捷方式
        try:
            startup_folder = os.path.join(
                os.path.expanduser('~'),
                'AppData',
                'Roaming',
                'Microsoft',
                'Windows',
                'Start Menu',
                'Programs',
                'Startup'
            )

            shortcut_path = os.path.join(startup_folder, "copy-cat.lnk")
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                write_status("启动文件夹快捷方式已删除")
        except:
            pass

        # 删除安装标志文件
        if os.path.exists('installed.flag'):
            os.remove('installed.flag')

        write_status("卸载完成")
        return True

    except Exception as e:
        write_status(f"卸载过程出错: {str(e)}")
        return False


def show_help():
    """显示帮助信息"""
    help_text = """
copy-cat - 后台服务版

使用方法:
  python main_hidden.py             启动后台监控
  python main_hidden.py install     安装为开机自启动
  python main_hidden.py uninstall   移除开机自启动
  python main_hidden.py help        显示此帮助
  python main_hidden.py gui         显示配置界面

后台运行:
  程序会在后台无窗口运行，所有信息记录到日志文件:
  - copy_cat_service.log    # 运行日志
  - copy_cat_status.log     # 状态日志
  - service_error.log       # 错误日志

开机自启动:
  安装后，程序会在用户登录时自动启动，无任何界面。

查看状态:
  查看日志文件了解程序运行状态。
"""
    print(help_text)


def show_gui():
    """显示简单的配置界面"""
    import tkinter as tk
    from tkinter import messagebox, ttk

    def on_install():
        if install_service():
            messagebox.showinfo("成功", "已安装为开机自启动")
        else:
            messagebox.showerror("错误", "安装失败，请查看日志")

    def on_uninstall():
        if uninstall_service():
            messagebox.showinfo("成功", "已移除开机自启动")
        else:
            messagebox.showerror("错误", "卸载失败，请查看日志")

    def on_start():
        messagebox.showinfo("提示", "程序将在后台启动，请查看日志文件")
        root.destroy()
        main()

    def on_exit():
        root.destroy()

    root = tk.Tk()
    root.title("copy-cat")
    root.geometry("400x300")

    # 标题
    title_label = tk.Label(root, text="copy-cat", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)

    # 说明
    info_label = tk.Label(root, text="一个后台运行的USB文件监控程序", wraplength=350)
    info_label.pack(pady=10)

    # 按钮框架
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    # 按钮
    btn_install = tk.Button(button_frame, text="安装为开机启动", command=on_install, width=20)
    btn_install.pack(pady=5)

    btn_uninstall = tk.Button(button_frame, text="移除开机启动", command=on_uninstall, width=20)
    btn_uninstall.pack(pady=5)

    btn_start = tk.Button(button_frame, text="启动监控", command=on_start, width=20)
    btn_start.pack(pady=5)

    btn_exit = tk.Button(button_frame, text="退出", command=on_exit, width=20)
    btn_exit.pack(pady=5)

    # 状态栏
    status_bar = tk.Label(root, text="状态: 就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    root.mainloop()


if __name__ == "__main__":
    # 处理命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg == "install":
            install_service()
        elif arg == "uninstall":
            uninstall_service()
        elif arg == "help" or arg == "-h" or arg == "--help":
            show_help()
        elif arg == "gui":
            show_gui()
        elif arg == "debug":
            # 调试模式：显示控制台
            if sys.platform == "win32":
                import ctypes

                ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)
            main()
        else:
            print(f"未知参数: {arg}")
            print("使用 'help' 查看帮助")
    else:
        # 无参数：后台运行
        main()