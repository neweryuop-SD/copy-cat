"""
增强版自启动管理模块
支持中文界面，提供更多功能
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, List, Tuple
import subprocess

class EnhancedAutoStartManager:
    """增强的自启动管理器"""

    def __init__(self, app_name: str = "USBBackup"):
        self.app_name = app_name
        self.startup_folder = self._get_startup_folder()
        self.config_file = Path("autostart_config.json")
        self._load_config()

    def _load_config(self):
        """加载配置"""
        default_config = {
            "app_name": "USBBackup",
            "exe_path": "",
            "args": "",
            "hidden_mode": True,
            "created_time": "",
            "last_modified": ""
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except:
                self.config = default_config
        else:
            self.config = default_config

    def _save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False

    def _get_startup_folder(self) -> Optional[Path]:
        """获取启动文件夹"""
        try:
            # 方法1: 使用环境变量
            appdata = os.environ.get('APPDATA', '')
            if appdata:
                startup_path = Path(appdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
                if startup_path.exists():
                    return startup_path

            # 方法2: 使用shell命令
            try:
                result = subprocess.run(
                    ['powershell', '-Command', '([Environment]::GetFolderPath("Startup"))'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                if result.returncode == 0:
                    startup_path = Path(result.stdout.strip())
                    if startup_path.exists():
                        return startup_path
            except:
                pass

            # 方法3: 使用已知路径
            user_profile = os.environ.get('USERPROFILE', '')
            if user_profile:
                startup_path = Path(user_profile) / 'AppData' / 'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
                if startup_path.exists():
                    return startup_path

            return None

        except Exception as e:
            print(f"获取启动文件夹失败: {e}")
            return None

    def setup_autostart(self, exe_path: str = "", args: str = "") -> Tuple[bool, str]:
        """设置开机自启动"""
        try:
            if not self.startup_folder:
                return False, "无法找到启动文件夹"

            # 如果没有提供exe_path，使用当前程序
            if not exe_path:
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    exe_path = os.path.abspath(sys.argv[0])

            # 确保路径是绝对路径
            exe_path = os.path.abspath(exe_path)

            # 创建批处理文件内容
            if exe_path.endswith('.py'):
                python_exe = sys.executable
                command = f'"{python_exe}" "{exe_path}"'
            else:
                command = f'"{exe_path}"'

            if args:
                command += f' {args}'

            # 如果启用隐藏模式，使用start /B
            if self.config.get("hidden_mode", True):
                bat_content = f'''@echo off
REM USB文件备份系统 - 自启动脚本
REM 创建时间: {self._get_current_time()}

chcp 65001 >nul
title USB备份系统
echo 正在启动USB文件备份系统...
start "" /B {command}
exit
'''
            else:
                bat_content = f'''@echo off
REM USB文件备份系统 - 自启动脚本
REM 创建时间: {self._get_current_time()}

chcp 65001 >nul
title USB备份系统
echo 正在启动USB文件备份系统...
{command}
pause
'''

            # 保存批处理文件
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

            # 更新配置
            self.config.update({
                "app_name": self.app_name,
                "exe_path": exe_path,
                "args": args,
                "hidden_mode": self.config.get("hidden_mode", True),
                "created_time": self._get_current_time(),
                "last_modified": self._get_current_time(),
                "bat_path": str(bat_path)
            })
            self._save_config()

            return True, f"自启动设置成功: {bat_path}"

        except Exception as e:
            return False, f"设置自启动失败: {e}"

    def remove_autostart(self) -> Tuple[bool, str, List[str]]:
        """移除开机自启动"""
        removed_files = []
        try:
            if not self.startup_folder:
                return False, "无法找到启动文件夹", removed_files

            # 要查找的文件名模式
            patterns = [
                f"{self.app_name}.bat",
                f"{self.app_name}.lnk",
                "USBBackup.bat",
                "USBBackup.lnk",
                "USB_File_Backup.bat",
                "USB_File_Backup.lnk"
            ]

            # 查找并删除文件
            for pattern in patterns:
                file_path = self.startup_folder / pattern
                if file_path.exists():
                    try:
                        file_path.unlink()
                        removed_files.append(pattern)
                        print(f"已删除: {pattern}")
                    except Exception as e:
                        print(f"删除失败 {pattern}: {e}")

            # 删除配置文件
            if self.config_file.exists():
                try:
                    self.config_file.unlink()
                    removed_files.append("autostart_config.json")
                except:
                    pass

            if removed_files:
                return True, f"成功移除 {len(removed_files)} 个自启动文件", removed_files
            else:
                return True, "未找到自启动文件", removed_files

        except Exception as e:
            return False, f"移除自启动失败: {e}", removed_files

    def check_autostart(self) -> Tuple[bool, List[str]]:
        """检查自启动状态"""
        found_files = []
        try:
            if not self.startup_folder:
                return False, found_files

            # 查找相关文件
            for file_path in self.startup_folder.glob("*"):
                filename = file_path.name.lower()
                if ("usbbackup" in filename or
                    "usb_file" in filename or
                    "usb backup" in filename.lower()):
                    found_files.append(file_path.name)

            return len(found_files) > 0, found_files

        except Exception as e:
            print(f"检查自启动失败: {e}")
            return False, found_files

    def open_startup_folder(self) -> bool:
        """打开启动文件夹"""
        try:
            if self.startup_folder:
                os.startfile(self.startup_folder)
                return True
            else:
                # 尝试用shell命令打开
                os.system('start shell:startup')
                return True
        except:
            return False

    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def create_manual_guide(self):
        """创建手动设置指南"""
        guide = f"""
        ========================================
        USB文件备份系统 - 手动自启动设置指南
        ========================================
        
        启动文件夹位置:
        {self.startup_folder or "C:\\Users\\[用户名]\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"}
        
        手动设置步骤:
        1. 打开启动文件夹（按 Win+R，输入: shell:startup）
        2. 创建新的批处理文件（例如: USBBackup.bat）
        3. 文件内容:
        
        @echo off
        chcp 65001 >nul
        start "" /B "{sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]}"
        exit
        
        4. 保存文件并设置为隐藏属性
        
        手动移除步骤:
        1. 打开启动文件夹
        2. 删除所有与USB备份相关的.bat和.lnk文件
        3. 重启电脑确认
        
        ========================================
        """
        return guide

def main():
    """命令行界面"""
    import argparse

    parser = argparse.ArgumentParser(
        description="USB文件备份系统 - 自启动管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python autostart_manager.py --setup
  python autostart_manager.py --remove
  python autostart_manager.py --check
  python autostart_manager.py --open
        """
    )

    parser.add_argument("--setup", action="store_true", help="设置开机自启动")
    parser.add_argument("--remove", action="store_true", help="移除开机自启动")
    parser.add_argument("--check", action="store_true", help="检查自启动状态")
    parser.add_argument("--open", action="store_true", help="打开启动文件夹")
    parser.add_argument("--guide", action="store_true", help="显示手动设置指南")
    parser.add_argument("--exe", type=str, help="指定可执行文件路径")
    parser.add_argument("--args", type=str, default="", help="启动参数")

    args = parser.parse_args()

    # 设置控制台编码为UTF-8
    if sys.platform == "win32":
        os.system("chcp 65001 >nul")

    manager = EnhancedAutoStartManager()

    print("=" * 60)
    print("USB文件备份系统 - 自启动管理工具")
    print("=" * 60)

    if args.setup:
        print("[信息] 正在设置开机自启动...")
        success, message = manager.setup_autostart(args.exe, args.args)
        if success:
            print(f"[成功] {message}")
        else:
            print(f"[失败] {message}")

    elif args.remove:
        print("[信息] 正在移除开机自启动...")
        success, message, files = manager.remove_autostart()
        if success:
            print(f"[成功] {message}")
            if files:
                print("移除的文件:")
                for f in files:
                    print(f"  - {f}")
        else:
            print(f"[失败] {message}")

    elif args.check:
        print("[信息] 检查自启动状态...")
        is_set, files = manager.check_autostart()
        if is_set:
            print("[警告] 已设置自启动")
            print("找到的文件:")
            for f in files:
                print(f"  - {f}")
        else:
            print("[信息] 未设置自启动")

    elif args.open:
        print("[信息] 正在打开启动文件夹...")
        if manager.open_startup_folder():
            print("[成功] 已打开启动文件夹")
        else:
            print("[失败] 无法打开启动文件夹")

    elif args.guide:
        print(manager.create_manual_guide())

    else:
        # 交互模式
        print("\n请选择操作:")
        print("1. 设置开机自启动")
        print("2. 移除开机自启动")
        print("3. 检查自启动状态")
        print("4. 打开启动文件夹")
        print("5. 显示手动设置指南")
        print("6. 退出")

        try:
            choice = input("\n请输入选项 (1-6): ").strip()

            if choice == "1":
                exe_path = input("可执行文件路径 (直接回车使用当前程序): ").strip()
                args_str = input("启动参数 (直接回车跳过): ").strip()
                success, message = manager.setup_autostart(exe_path if exe_path else None, args_str)
                print(f"\n{message}")

            elif choice == "2":
                success, message, files = manager.remove_autostart()
                print(f"\n{message}")

            elif choice == "3":
                is_set, files = manager.check_autostart()
                if is_set:
                    print("\n[警告] 已设置自启动")
                    for f in files:
                        print(f"  - {f}")
                else:
                    print("\n[信息] 未设置自启动")

            elif choice == "4":
                if manager.open_startup_folder():
                    print("\n[成功] 已打开启动文件夹")
                else:
                    print("\n[失败] 无法打开启动文件夹")

            elif choice == "5":
                print(manager.create_manual_guide())

            elif choice == "6":
                print("\n再见！")
                return

            else:
                print("\n无效选择")

        except KeyboardInterrupt:
            print("\n\n操作取消")
        except Exception as e:
            print(f"\n发生错误: {e}")

    print("\n" + "=" * 60)
    input("按回车键退出...")

if __name__ == "__main__":
    main()
