"""
开机自启动管理模块 - 无需管理员权限
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional

try:
    import pythoncom
    from win32com.shell import shell, shellcon

    WINDOWS_COM_AVAILABLE = True
except ImportError:
    WINDOWS_COM_AVAILABLE = False


class AutoStartManager:
    """自启动管理器（无需管理员权限）"""

    def __init__(self, app_name: str = "USBBackup"):
        self.app_name = app_name
        self.startup_folder = self._get_startup_folder()

    def _get_startup_folder(self) -> Optional[Path]:
        """获取当前用户的启动文件夹"""
        try:
            # 方法1: 使用环境变量（最可靠）
            appdata = os.environ.get('APPDATA', '')
            if appdata:
                startup_path = Path(appdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
                if startup_path.exists():
                    return startup_path

            # 方法2: 尝试使用shell
            if WINDOWS_COM_AVAILABLE:
                try:
                    from win32com.client import Dispatch
                    shell = Dispatch("WScript.Shell")
                    startup_path = shell.SpecialFolders("Startup")
                    return Path(startup_path)
                except:
                    pass

            # 方法3: 使用已知路径
            user_profile = os.environ.get('USERPROFILE', '')
            if user_profile:
                startup_path = Path(
                    user_profile) / 'AppData' / 'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
                if startup_path.exists():
                    return startup_path

            return None

        except Exception as e:
            print(f"[ERROR] 获取启动文件夹失败: {e}")
            return None

    def set_autostart(self, exe_path: str, args: str = "") -> bool:
        """设置开机自启动"""
        try:
            if not self.startup_folder:
                print("[ERROR] 无法找到启动文件夹")
                return False

            # 确保路径是绝对路径
            exe_path = os.path.abspath(exe_path)

            # 如果是Python脚本，需要指定Python解释器
            if exe_path.endswith('.py'):
                python_exe = sys.executable
                target = f'"{python_exe}" "{exe_path}"'
                if args:
                    target += f" {args}"
            else:
                target = f'"{exe_path}"'
                if args:
                    target += f" {args}"

            # 创建批处理文件（最简单可靠的方法）
            return self._create_bat_file(target)

        except Exception as e:
            print(f"[ERROR] 设置自启动失败: {e}")
            return False

    def _create_bat_file(self, target: str) -> bool:
        """创建批处理文件到启动文件夹"""
        try:
            bat_content = f'@echo off\nstart "" /B {target}\n'
            bat_path = self.startup_folder / f"{self.app_name}.bat"

            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)

            # 隐藏批处理文件
            try:
                import ctypes
                FILE_ATTRIBUTE_HIDDEN = 0x02
                ctypes.windll.kernel32.SetFileAttributesW(str(bat_path), FILE_ATTRIBUTE_HIDDEN)
            except:
                pass

            print(f"[INFO] 已创建自启动批处理文件: {bat_path}")
            return True

        except Exception as e:
            print(f"[ERROR] 创建批处理文件失败: {e}")
            return False

    def _create_shortcut(self, target: str) -> bool:
        """创建快捷方式（备用方法）"""
        if not WINDOWS_COM_AVAILABLE:
            return False

        try:
            shortcut_path = self.startup_folder / f"{self.app_name}.lnk"

            shortcut = pythoncom.CoCreateInstance(
                shell.CLSID_ShellLink,
                None,
                pythoncom.CLSCTX_INPROC_SERVER,
                shell.IID_IShellLink
            )

            # 设置目标路径
            shortcut.SetPath(sys.executable)

            # 如果是Python脚本，设置参数
            if target.endswith('.py'):
                shortcut.SetArguments(f'"{target}"')

            # 设置工作目录
            shortcut.SetWorkingDirectory(str(Path(target).parent))

            # 设置描述
            shortcut.SetDescription("USB文件监控备份系统")

            # 保存快捷方式
            persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
            persist_file.Save(str(shortcut_path), 0)

            return True

        except Exception as e:
            print(f"[ERROR] 创建快捷方式失败: {e}")
            return False

    def remove_autostart(self) -> bool:
        """移除开机自启动"""
        try:
            if not self.startup_folder:
                return False

            removed = False

            # 删除批处理文件
            bat_path = self.startup_folder / f"{self.app_name}.bat"
            if bat_path.exists():
                bat_path.unlink()
                removed = True

            # 删除快捷方式
            shortcut_path = self.startup_folder / f"{self.app_name}.lnk"
            if shortcut_path.exists():
                shortcut_path.unlink()
                removed = True

            if removed:
                print("[INFO] 已移除开机自启动")

            return removed

        except Exception as e:
            print(f"[ERROR] 移除自启动失败: {e}")
            return False

    def is_autostart_set(self) -> bool:
        """检查是否已设置自启动"""
        try:
            if not self.startup_folder:
                return False

            bat_path = self.startup_folder / f"{self.app_name}.bat"
            shortcut_path = self.startup_folder / f"{self.app_name}.lnk"

            return bat_path.exists() or shortcut_path.exists()

        except:
            return False


def setup_autostart_manually():
    """手动设置自启动的说明"""
    print("\n" + "=" * 60)
    print("手动设置开机自启动")
    print("=" * 60)

    # 获取启动文件夹路径
    manager = AutoStartManager()
    if manager.startup_folder:
        print(f"启动文件夹: {manager.startup_folder}")
    else:
        print("启动文件夹: C:\\Users\\[用户名]\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")

    print("\n手动设置步骤:")
    print("1. 打开启动文件夹（Win+R，输入: shell:startup）")
    print("2. 创建新的快捷方式或批处理文件")
    print("3. 目标指向本程序")
    print("\n或运行程序时添加 --setup 参数尝试自动设置")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="开机自启动管理")
    parser.add_argument("--setup", action="store_true", help="设置开机自启动")
    parser.add_argument("--remove", action="store_true", help="移除开机自启动")
    parser.add_argument("--check", action="store_true", help="检查自启动状态")
    parser.add_argument("--exe", type=str, help="可执行文件路径")
    parser.add_argument("--args", type=str, default="", help="启动参数")

    args = parser.parse_args()

    manager = AutoStartManager()

    if args.setup:
        if args.exe:
            success = manager.set_autostart(args.exe, args.args)
            print(f"设置结果: {'成功' if success else '失败'}")
        else:
            print("请使用 --exe 参数指定可执行文件路径")
    elif args.remove:
        success = manager.remove_autostart()
        print(f"移除结果: {'成功' if success else '失败'}")
    elif args.check:
        is_set = manager.is_autostart_set()
        print(f"自启动状态: {'已设置' if is_set else '未设置'}")
    else:
        setup_autostart_manually()