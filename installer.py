import os
import sys
import winreg
import ctypes
import subprocess
from pathlib import Path
import json


class Installer:
    def __init__(self, app_name="USBMonitor"):
        self.app_name = app_name
        self.app_path = os.path.abspath(sys.argv[0])
        self.user_startup_dir = self.get_user_startup_dir()

    def get_user_startup_dir(self):
        """获取当前用户的启动文件夹（不需要管理员权限）"""
        # Windows启动文件夹路径
        startup_path = os.path.join(
            os.path.expanduser('~'),
            'AppData',
            'Roaming',
            'Microsoft',
            'Windows',
            'Start Menu',
            'Programs',
            'Startup'
        )
        return startup_path

    def add_to_startup(self):
        """添加到开机启动（使用启动文件夹，不需要管理员权限）"""
        try:
            # 创建快捷方式到启动文件夹
            import winshell
            from win32com.client import Dispatch

            # 创建快捷方式
            startup_shortcut = os.path.join(self.user_startup_dir, f"{self.app_name}.lnk")

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(startup_shortcut)

            # 设置目标路径
            if self.app_path.endswith('.py'):
                # Python脚本 - 使用pythonw.exe运行（无窗口）
                pythonw_path = sys.executable.replace('python.exe', 'pythonw.exe')
                shortcut.TargetPath = pythonw_path
                shortcut.Arguments = f'"{self.app_path}"'
            else:
                # 可执行文件
                shortcut.TargetPath = self.app_path

            # 设置工作目录
            shortcut.WorkingDirectory = os.path.dirname(self.app_path)

            # 设置运行方式（最小化）
            shortcut.WindowStyle = 7  # 7=最小化

            shortcut.save()

            print(f"✓ 已添加到开机启动: {startup_shortcut}")
            return True

        except ImportError:
            # 如果winshell不可用，使用传统方法
            try:
                return self.add_to_startup_registry()
            except:
                print("✗ 无法创建启动项，请手动将程序添加到启动文件夹")
                return False
        except Exception as e:
            print(f"✗ 添加开机启动失败: {str(e)}")
            return False

    def add_to_startup_registry(self):
        """使用注册表添加到开机启动（当前用户，不需要管理员权限）"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )

            if self.app_path.endswith('.py'):
                pythonw_path = sys.executable.replace('python.exe', 'pythonw.exe')
                command = f'"{pythonw_path}" "{self.app_path}"'
            else:
                command = f'"{self.app_path}"'

            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)

            print(f"✓ 已添加到开机启动(注册表): {command}")
            return True
        except Exception as e:
            print(f"✗ 注册表启动项添加失败: {str(e)}")
            return False

    def remove_from_startup(self):
        """从开机启动移除"""
        try:
            # 尝试删除启动文件夹中的快捷方式
            startup_shortcut = os.path.join(self.user_startup_dir, f"{self.app_name}.lnk")
            if os.path.exists(startup_shortcut):
                os.remove(startup_shortcut)
                print(f"✓ 已删除启动快捷方式: {startup_shortcut}")

            # 尝试删除注册表启动项
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_SET_VALUE
                )
                winreg.DeleteValue(key, self.app_name)
                winreg.CloseKey(key)
                print("✓ 已从注册表启动项移除")
            except:
                pass

            return True
        except Exception as e:
            print(f"✗ 移除开机启动失败: {str(e)}")
            return False

    def create_config_file(self):
        """创建配置文件"""
        try:
            from config import Config
            config = Config()
            print("✓ 配置文件已创建")
            return True
        except:
            print("✗ 创建配置文件失败")
            return False

    def add_firewall_exception(self):
        """添加防火墙例外（如果程序有网络功能）"""
        try:
            # 只有在程序有网络功能时才需要
            # 这里只是示例，实际使用时需要根据程序功能调整
            print("ℹ 程序无网络功能，无需防火墙例外")
            return True
        except:
            return False

    def create_shortcut_on_desktop(self):
        """在桌面创建快捷方式（可选）"""
        try:
            import winshell
            from win32com.client import Dispatch

            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, f"{self.app_name}.lnk")

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(shortcut_path)

            if self.app_path.endswith('.py'):
                pythonw_path = sys.executable.replace('python.exe', 'pythonw.exe')
                shortcut.TargetPath = pythonw_path
                shortcut.Arguments = f'"{self.app_path}"'
            else:
                shortcut.TargetPath = self.app_path

            shortcut.WorkingDirectory = os.path.dirname(self.app_path)
            shortcut.Description = "USB监控程序"
            shortcut.save()

            print(f"✓ 桌面快捷方式已创建: {shortcut_path}")
            return True
        except:
            print("✗ 创建桌面快捷方式失败")
            return False

    def install(self):
        """安装程序（不需要管理员权限）"""
        print("正在安装USB监控程序...")
        print("-" * 40)

        # 1. 创建配置文件
        self.create_config_file()

        # 2. 添加到开机启动
        self.add_to_startup()

        # 3. 创建桌面快捷方式（可选）
        create_desktop_shortcut = input("是否在桌面创建快捷方式? (y/n): ")
        if create_desktop_shortcut.lower() == 'y':
            self.create_shortcut_on_desktop()

        # 4. 添加防火墙例外
        self.add_firewall_exception()

        print("-" * 40)
        print("安装完成！")
        print(f"配置文件: config.ini")
        print(f"备份文件夹: {os.path.expanduser('~')}\\USB_Backup")
        print("\n注意：程序将在下次登录时自动启动")

    def uninstall(self):
        """卸载程序"""
        print("正在卸载USB监控程序...")
        print("-" * 40)

        # 1. 从开机启动移除
        self.remove_from_startup()

        # 2. 删除桌面快捷方式
        try:
            import winshell
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, f"{self.app_name}.lnk")
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                print(f"✓ 已删除桌面快捷方式")
        except:
            pass

        # 3. 询问是否删除配置文件和数据
        keep_data = input("是否保留配置文件和备份数据? (y/n): ")
        if keep_data.lower() == 'n':
            try:
                # 删除配置文件
                if os.path.exists('config.ini'):
                    os.remove('config.ini')
                    print("✓ 已删除配置文件")

                # 删除日志文件
                if os.path.exists('usb_monitor.log'):
                    os.remove('usb_monitor.log')
                    print("✓ 已删除日志文件")
            except:
                print("✗ 删除文件失败，请手动删除")

        print("-" * 40)
        print("卸载完成！")
        print("注意：备份文件夹需要手动删除（如果不再需要）")