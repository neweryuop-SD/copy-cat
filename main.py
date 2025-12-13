#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
USB监控和文件备份程序 - 安全加固版
安全特性：
1. 不需要管理员权限
2. 防止路径遍历攻击
3. 文件类型安全检查
4. 火绒安全兼容
5. 限制文件大小和类型
"""

import sys
import os
import atexit
import traceback
from config import Config
from logger import Logger
from file_handler import FileHandler
from monitor import USBMoniTor
from installer import Installer


def setup_exception_handler():
    """设置全局异常处理器"""

    def handle_exception(exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        # 记录到错误日志
        try:
            error_log = "error.log"
            with open(error_log, 'a', encoding='utf-8') as f:
                f.write(f"\n{'=' * 50}\n")
                f.write(f"崩溃时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"错误信息:\n{error_msg}\n")
        except:
            pass

        # 显示用户友好的错误信息
        print(f"\n程序遇到错误，已记录到 error.log")
        print("错误信息:", str(exc_value))

        # 退出程序
        sys.exit(1)

    # 设置异常处理器
    sys.excepthook = handle_exception


def cleanup():
    """清理函数"""
    print("\n正在清理资源...")


def check_prerequisites():
    """检查运行环境"""
    try:
        import psutil
        import win32api

        # 检查是否安装了必要的模块
        required_modules = ['psutil', 'pywin32']
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                print(f"错误: 缺少必要模块 {module}")
                print("请运行: pip install psutil pywin32")
                return False

        return True
    except Exception as e:
        print(f"环境检查失败: {str(e)}")
        return False


def create_firewall_compatibility_file():
    """创建火绒安全兼容性说明文件"""
    try:
        firewall_info = """
火绒安全软件兼容性说明
========================

本程序为合法的USB文件备份工具，可能会触发火绒安全的以下检测：

1. 文件监控行为 - 正常（文件备份功能）
2. 注册表修改 - 正常（开机启动设置）
3. 进程创建 - 正常（程序正常运行）

如何添加到火绒信任列表：
1. 打开火绒安全软件
2. 进入"防护中心"
3. 点击"高级防护"
4. 选择"信任程序"
5. 添加本程序到信任列表

程序功能：
- 监控USB设备插入
- 备份指定类型的文件
- 不收集个人信息
- 不连接网络
"""

        with open("火绒安全兼容说明.txt", "w", encoding="utf-8") as f:
            f.write(firewall_info)

        print("✓ 已创建安全软件兼容性说明文件")
        return True
    except:
        return False


def show_security_notice():
    """显示安全声明"""
    notice = """
安全声明
========

本程序仅用于合法的USB文件备份目的，具有以下安全特性：

1. 无需管理员权限运行
2. 不收集个人隐私信息
3. 仅备份用户指定的文件类型
4. 不包含任何恶意代码
5. 源代码完全公开透明

隐私保护：
- 所有文件保存在用户本地
- 不传输任何数据到网络
- 用户可以随时查看和删除备份文件

使用前请确保：
1. 您有权限备份目标文件
2. 遵守相关法律法规
3. 尊重他人隐私权

按 Enter 继续，或按 Ctrl+C 退出...
"""
    print(notice)
    try:
        input()
    except KeyboardInterrupt:
        print("\n用户取消操作")
        sys.exit(0)


def main():
    """主函数"""
    print("=" * 60)
    print("USB监控和文件备份程序 - 安全加固版")
    print("=" * 60)

    # 设置异常处理
    setup_exception_handler()

    # 注册清理函数
    atexit.register(cleanup)

    # 检查运行环境
    if not check_prerequisites():
        sys.exit(1)

    # 显示安全声明
    show_security_notice()

    # 创建安全软件兼容性说明
    create_firewall_compatibility_file()

    # 检查命令行参数
    if len(sys.argv) > 1:
        handle_command_line(sys.argv[1])
        return

    # 正常启动监控
    start_monitoring()


def handle_command_line(command):
    """处理命令行参数"""
    installer = Installer()

    command = command.lower()

    if command in ['install', '-install', '--install']:
        installer.install()
    elif command in ['uninstall', '-uninstall', '--uninstall']:
        installer.uninstall()
    elif command in ['help', '-h', '--help', '/?']:
        show_help()
    elif command in ['version', '-v', '--version']:
        show_version()
    elif command in ['config', '-config', '--config']:
        edit_config()
    else:
        print(f"未知命令: {command}")
        show_help()


def show_help():
    """显示帮助信息"""
    help_text = """
USB监控程序 - 使用帮助

基本命令:
  main.py                    启动监控程序
  main.py install           安装程序（开机自启动）
  main.py uninstall         卸载程序
  main.py config            编辑配置文件
  main.py help              显示此帮助信息
  main.py version           显示版本信息

配置文件:
  程序使用 config.ini 作为配置文件，可以修改：
  - 要备份的文件类型（keywords）
  - 备份目标文件夹（target_folder）
  - 检查间隔时间（check_interval）
  - 日志设置等

安全特性:
  - 无需管理员权限
  - 防止路径遍历攻击
  - 文件类型安全检查
  - 兼容火绒等安全软件

注意事项:
  1. 请遵守法律法规使用本程序
  2. 仅备份您有权限的文件
  3. 定期检查备份文件夹
"""
    print(help_text)


def show_version():
    """显示版本信息"""
    version = """
USB监控程序 版本 2.0

安全加固版特性:
- 无需管理员权限
- 增强的安全检查
- 火绒安全兼容
- 文件类型验证
- 防止路径遍历

作者: 安全开发团队
日期: 2024
许可证: 仅限合法使用
"""
    print(version)


def edit_config():
    """编辑配置文件"""
    try:
        import subprocess

        config_file = "config.ini"
        if not os.path.exists(config_file):
            from config import Config
            config = Config()
            print("已创建默认配置文件")

        # 尝试用记事本打开配置文件
        os.system(f"notepad {config_file}")
        print("配置文件已打开，修改后请保存")

    except Exception as e:
        print(f"打开配置文件失败: {str(e)}")


def start_monitoring():
    """启动监控程序"""
    try:
        # 初始化配置
        config = Config()

        # 初始化日志
        logger = Logger(config)
        logger.log_info("程序启动 - 安全加固版")

        # 初始化文件处理器
        file_handler = FileHandler(config, logger)

        # 初始化监控器
        monitor = USBMoniTor(config, logger, file_handler)

        print("\n" + "=" * 60)
        print("监控程序正在运行...")
        print("安全特性已启用:")
        print("  ✓ 文件类型安全检查")
        print("  ✓ 路径遍历防护")
        print("  ✓ 文件大小限制")
        print("  ✓ 火绒安全兼容模式")
        print(f"\n监控文件夹: {config.get_target_folder()}")
        print(f"安全文件类型: {', '.join(config.get_keywords())}")
        print(f"检查间隔: {config.get_check_interval()}秒")
        print(f"最大文件大小: {config.get_max_file_size()} MB")
        print("\n按 Ctrl+C 停止程序")
        print("=" * 60 + "\n")

        # 开始监控
        monitor.start_monitoring()

    except KeyboardInterrupt:
        print("\n程序已安全停止")
        if 'logger' in locals():
            logger.log_info("程序被用户停止")
    except Exception as e:
        print(f"\n程序遇到错误: {str(e)}")
        if 'logger' in locals():
            logger.log_error(f"程序异常: {str(e)}")

        # 显示错误日志位置
        print("详细信息请查看 error.log 文件")


if __name__ == "__main__":
    main()