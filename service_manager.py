#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
copy-cat - 服务管理器
用于安装、卸载、启动、停止后台服务
"""

import os
import sys
import time
import psutil
import subprocess
from datetime import datetime


class ServiceManager:
    def __init__(self):
        self.service_name = "copy-cat"
        self.log_file = "service_manager.log"

    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + "\n")

    def is_service_running(self):
        """检查服务是否在运行"""
        for proc in psutil.process_iter(['name', 'exe', 'cmdline']):
            try:
                # 检查进程
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any('main_hidden' in str(arg) for arg in cmdline):
                        return True, proc.pid

                # 检查打包的exe
                if proc.info['exe'] and 'copy-cat' in proc.info['exe']:
                    return True, proc.pid

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return False, None

    def install_service(self):
        """安装为开机自启动"""
        self.log("正在安装开机自启动...")

        try:
            import winreg

            # 获取当前路径
            if getattr(sys, 'frozen', False):
                # 打包的exe
                exe_path = sys.executable
            else:
                # Python脚本
                pythonw_path = sys.executable.replace('python.exe', 'pythonw.exe')
                script_path = os.path.abspath('main_hidden.py')
                exe_path = f'"{pythonw_path}" "{script_path}"'

            # 添加到注册表
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, self.service_name, 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)

            self.log(f"开机自启动安装成功: {exe_path}")

            # 创建安装记录
            with open('installed.txt', 'w', encoding='utf-8') as f:
                f.write(f"安装时间: {datetime.now()}\n")
                f.write(f"启动路径: {exe_path}\n")
                f.write(f"服务名称: {self.service_name}\n")

            return True

        except Exception as e:
            self.log(f"安装失败: {str(e)}")
            return False

    def uninstall_service(self):
        """移除开机自启动"""
        self.log("正在移除开机自启动...")

        try:
            import winreg

            # 从注册表移除
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, self.service_name)
                winreg.CloseKey(key)
                self.log("注册表项已移除")
            except WindowsError:
                self.log("注册表中未找到服务项")

            # 删除安装记录
            if os.path.exists('installed.txt'):
                os.remove('installed.txt')

            self.log("开机自启动已移除")
            return True

        except Exception as e:
            self.log(f"移除失败: {str(e)}")
            return False

    def start_service(self, hidden=True):
        """启动服务"""
        self.log("正在启动服务...")

        is_running, pid = self.is_service_running()
        if is_running:
            self.log(f"服务已在运行，PID: {pid}")
            return True

        try:
            if getattr(sys, 'frozen', False):
                # 打包的exe
                if hidden:
                    # 无窗口启动
                    subprocess.Popen([sys.executable],
                                     creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    subprocess.Popen([sys.executable])
            else:
                # Python脚本
                if hidden:
                    pythonw_path = sys.executable.replace('python.exe', 'pythonw.exe')
                    script_path = 'main_hidden.py'
                    subprocess.Popen([pythonw_path, script_path],
                                     creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    python_path = sys.executable
                    script_path = 'main_hidden.py'
                    subprocess.Popen([python_path, script_path])

            # 等待并检查是否启动成功
            time.sleep(2)
            is_running, pid = self.is_service_running()

            if is_running:
                self.log(f"服务启动成功，PID: {pid}")
                return True
            else:
                self.log("服务启动失败")
                return False

        except Exception as e:
            self.log(f"启动失败: {str(e)}")
            return False

    def stop_service(self):
        """停止服务"""
        self.log("正在停止服务...")

        is_running, pid = self.is_service_running()
        if not is_running:
            self.log("服务未在运行")
            return True

        try:
            # 结束进程
            proc = psutil.Process(pid)
            proc.terminate()

            # 等待进程结束
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                # 强制结束
                proc.kill()

            self.log("服务已停止")
            return True

        except Exception as e:
            self.log(f"停止失败: {str(e)}")
            return False

    def show_status(self):
        """显示服务状态"""
        is_running, pid = self.is_service_running()

        print("\n" + "=" * 50)
        print("copy-cat - 服务状态")
        print("=" * 50)

        if is_running:
            print(f"状态: 运行中 (PID: {pid})")
        else:
            print("状态: 未运行")

        # 检查开机启动
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)

            try:
                value, _ = winreg.QueryValueEx(key, self.service_name)
                print(f"开机启动: 已启用")
                print(f"启动路径: {value}")
            except WindowsError:
                print(f"开机启动: 未启用")

            winreg.CloseKey(key)

        except:
            print("开机启动: 未知")

        # 检查日志文件
        log_files = ['copy_cat_service.log', 'copy_cat_status.log', 'service_error.log']
        print("\n日志文件:")
        for log_file in log_files:
            if os.path.exists(log_file):
                size = os.path.getsize(log_file)
                mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                print(f"  {log_file}: {size:,} 字节, 修改时间: {mtime}")
            else:
                print(f"  {log_file}: 不存在")

        print("=" * 50 + "\n")

        return is_running

    def show_menu(self):
        """显示管理菜单"""
        while True:
            print("\n" + "=" * 50)
            print("copy-cat - 服务管理器")
            print("=" * 50)
            print("1. 显示状态")
            print("2. 启动服务 (后台)")
            print("3. 停止服务")
            print("4. 安装为开机自启动")
            print("5. 移除开机自启动")
            print("6. 启动配置界面")
            print("7. 查看日志文件")
            print("8. 退出")
            print("=" * 50)

            try:
                choice = input("\n请选择操作 (1-8): ").strip()

                if choice == '1':
                    self.show_status()
                elif choice == '2':
                    self.start_service(hidden=True)
                elif choice == '3':
                    self.stop_service()
                elif choice == '4':
                    self.install_service()
                elif choice == '5':
                    self.uninstall_service()
                elif choice == '6':
                    self.start_config_gui()
                elif choice == '7':
                    self.view_logs()
                elif choice == '8':
                    print("退出服务管理器")
                    break
                else:
                    print("无效选择，请重新输入")

                input("\n按 Enter 继续...")

            except KeyboardInterrupt:
                print("\n\n用户中断")
                break
            except Exception as e:
                print(f"发生错误: {str(e)}")

    def start_config_gui(self):
        """启动配置界面"""
        self.log("启动配置界面...")

        try:
            if getattr(sys, 'frozen', False):
                # 如果是打包的exe，需要单独运行配置程序
                print("配置功能需要单独的程序")
            else:
                # 运行配置界面
                import subprocess
                subprocess.Popen([sys.executable, 'config_gui.py'])

        except Exception as e:
            self.log(f"启动配置界面失败: {str(e)}")
            print(f"错误: {str(e)}")

    def view_logs(self):
        """查看日志文件"""
        print("\n日志文件查看器")
        print("=" * 30)

        log_files = [
            ('服务管理日志', 'service_manager.log'),
            ('服务运行日志', 'copy_cat_service.log'),
            ('状态日志', 'copy_cat_status.log'),
            ('错误日志', 'service_error.log'),
            ('copy-cat日志', 'copy-cat.log')
        ]

        for i, (name, filename) in enumerate(log_files, 1):
            print(f"{i}. {name} ({filename})")

        print("0. 返回")

        try:
            choice = input("\n选择要查看的日志 (0-5): ").strip()
            if choice == '0':
                return

            index = int(choice) - 1
            if 0 <= index < len(log_files):
                filename = log_files[index][1]

                if os.path.exists(filename):
                    print(f"\n{'=' * 30}")
                    print(f"文件: {filename}")
                    print(f"{'=' * 30}\n")

                    with open(filename, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    # 显示最后100行
                    for line in lines[-100:]:
                        print(line.rstrip())

                    print(f"\n共 {len(lines)} 行，显示最后 100 行")
                else:
                    print(f"文件不存在: {filename}")
            else:
                print("无效选择")

        except Exception as e:
            print(f"查看日志失败: {str(e)}")


if __name__ == "__main__":
    manager = ServiceManager()

    # 检查命令行参数
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == "status":
            manager.show_status()
        elif cmd == "start":
            manager.start_service()
        elif cmd == "stop":
            manager.stop_service()
        elif cmd == "install":
            manager.install_service()
        elif cmd == "uninstall":
            manager.uninstall_service()
        elif cmd == "restart":
            manager.stop_service()
            time.sleep(1)
            manager.start_service()
        elif cmd == "help" or cmd == "-h" or cmd == "--help":
            print("""
copy-cat服务管理器

使用方法:
  python service_manager.py [命令]

命令:
  status      显示服务状态
  start       启动服务
  stop        停止服务
  restart     重启服务
  install     安装为开机自启动
  uninstall   移除开机自启动
  (无参数)    显示交互式菜单

示例:
  python service_manager.py start
  python service_manager.py status
            """)
        else:
            print(f"未知命令: {cmd}")
            print("使用 'help' 查看帮助")
    else:
        # 无参数：显示菜单
        manager.show_menu()