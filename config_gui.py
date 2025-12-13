#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
copy-cat - 配置界面
用于配置程序参数
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import configparser
import os
import sys


class ConfigGUI:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()

        # 加载或创建配置
        if os.path.exists(config_file):
            self.config.read(config_file, encoding='utf-8')
        else:
            self.create_default_config()

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("copy-cat - 配置")
        self.root.geometry("500x600")

        # 设置图标（如果有）
        try:
            self.root.iconbitmap('copy-cat.ico')
        except:
            pass

        self.create_widgets()

    def create_default_config(self):
        """创建默认配置"""
        self.config['Settings'] = {
            'keywords': '.doc,.docx,.pdf,.txt,.xlsx,.xls,.pptx,.ppt,.jpg,.png',
            'target_folder': 'C:\\copy-cat_backup',
            'check_interval': '5',
            'log_all_usb': 'true'
        }

        self.config['Logging'] = {
            'log_file': 'copy-cat.log',
            'log_level': 'INFO',
            'max_log_size': '10',
            'backup_count': '5'
        }

        self.config['Security'] = {
            'max_file_size': '100',
            'exclude_drives': 'C'
        }

        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def create_widgets(self):
        """创建界面控件"""

        # 创建Notebook（标签页）
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # 基本设置标签页
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text='基本设置')

        # 文件类型设置
        ttk.Label(basic_frame, text="要备份的文件类型（扩展名）:").grid(row=0, column=0, sticky='w', padx=10, pady=10)
        self.keywords_var = tk.StringVar(value=self.config['Settings'].get('keywords', ''))
        keywords_entry = ttk.Entry(basic_frame, textvariable=self.keywords_var, width=50)
        keywords_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        ttk.Label(basic_frame, text="用逗号分隔，如: .doc,.pdf,.jpg").grid(row=1, column=1, sticky='w', padx=10)

        # 目标文件夹
        ttk.Label(basic_frame, text="备份目标文件夹:").grid(row=2, column=0, sticky='w', padx=10, pady=10)
        self.target_var = tk.StringVar(value=self.config['Settings'].get('target_folder', ''))
        target_frame = ttk.Frame(basic_frame)
        target_frame.grid(row=2, column=1, padx=10, pady=10, sticky='ew')
        target_entry = ttk.Entry(target_frame, textvariable=self.target_var, width=40)
        target_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(target_frame, text="浏览...", command=self.browse_folder).pack(side='right', padx=(5, 0))

        # 检查间隔
        ttk.Label(basic_frame, text="检查间隔（秒）:").grid(row=3, column=0, sticky='w', padx=10, pady=10)
        self.interval_var = tk.StringVar(value=self.config['Settings'].get('check_interval', '5'))
        interval_spin = ttk.Spinbox(basic_frame, from_=1, to=60, textvariable=self.interval_var, width=10)
        interval_spin.grid(row=3, column=1, sticky='w', padx=10, pady=10)

        # 日志设置标签页
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text='日志设置')

        # 日志文件
        ttk.Label(log_frame, text="日志文件:").grid(row=0, column=0, sticky='w', padx=10, pady=10)
        self.log_file_var = tk.StringVar(value=self.config['Logging'].get('log_file', ''))
        log_file_entry = ttk.Entry(log_frame, textvariable=self.log_file_var, width=40)
        log_file_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        # 日志级别
        ttk.Label(log_frame, text="日志级别:").grid(row=1, column=0, sticky='w', padx=10, pady=10)
        self.log_level_var = tk.StringVar(value=self.config['Logging'].get('log_level', 'INFO'))
        log_level_combo = ttk.Combobox(log_frame, textvariable=self.log_level_var,
                                       values=['DEBUG', 'INFO', 'WARNING', 'ERROR'], width=15)
        log_level_combo.grid(row=1, column=1, sticky='w', padx=10, pady=10)

        # 安全设置标签页
        security_frame = ttk.Frame(notebook)
        notebook.add(security_frame, text='安全设置')

        # 最大文件大小
        ttk.Label(security_frame, text="最大文件大小（MB）:").grid(row=0, column=0, sticky='w', padx=10, pady=10)
        self.max_size_var = tk.StringVar(value=self.config['Security'].get('max_file_size', '100'))
        max_size_spin = ttk.Spinbox(security_frame, from_=1, to=1000, textvariable=self.max_size_var, width=10)
        max_size_spin.grid(row=0, column=1, sticky='w', padx=10, pady=10)

        # 排除的驱动器
        ttk.Label(security_frame, text="排除的驱动器:").grid(row=1, column=0, sticky='w', padx=10, pady=10)
        self.exclude_var = tk.StringVar(value=self.config['Security'].get('exclude_drives', 'C'))
        exclude_entry = ttk.Entry(security_frame, textvariable=self.exclude_var, width=20)
        exclude_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)
        ttk.Label(security_frame, text="用逗号分隔，如: C,D").grid(row=2, column=1, sticky='w', padx=10)

        # 操作按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill='x', padx=10, pady=10)

        # 按钮
        ttk.Button(button_frame, text="保存配置", command=self.save_config).pack(side='left', padx=5)
        ttk.Button(button_frame, text="恢复默认", command=self.restore_default).pack(side='left', padx=5)
        ttk.Button(button_frame, text="启动监控", command=self.start_monitor).pack(side='right', padx=5)
        ttk.Button(button_frame, text="退出", command=self.root.destroy).pack(side='right', padx=5)

    def browse_folder(self):
        """浏览文件夹"""
        folder = filedialog.askdirectory(title="选择备份目标文件夹")
        if folder:
            self.target_var.set(folder)

    def save_config(self):
        """保存配置"""
        try:
            # 更新配置
            self.config['Settings']['keywords'] = self.keywords_var.get()
            self.config['Settings']['target_folder'] = self.target_var.get()
            self.config['Settings']['check_interval'] = self.interval_var.get()

            self.config['Logging']['log_file'] = self.log_file_var.get()
            self.config['Logging']['log_level'] = self.log_level_var.get()

            self.config['Security']['max_file_size'] = self.max_size_var.get()
            self.config['Security']['exclude_drives'] = self.exclude_var.get()

            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)

            messagebox.showinfo("成功", "配置已保存")

        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")

    def restore_default(self):
        """恢复默认配置"""
        if messagebox.askyesno("确认", "确定要恢复默认配置吗？"):
            os.remove(self.config_file)
            self.create_default_config()
            self.config.read(self.config_file, encoding='utf-8')

            # 更新界面
            self.keywords_var.set(self.config['Settings'].get('keywords', ''))
            self.target_var.set(self.config['Settings'].get('target_folder', ''))
            self.interval_var.set(self.config['Settings'].get('check_interval', ''))
            self.log_file_var.set(self.config['Logging'].get('log_file', ''))
            self.log_level_var.set(self.config['Logging'].get('log_level', ''))
            self.max_size_var.set(self.config['Security'].get('max_file_size', ''))
            self.exclude_var.set(self.config['Security'].get('exclude_drives', ''))

            messagebox.showinfo("成功", "已恢复默认配置")

    def start_monitor(self):
        """启动监控程序"""
        # 先保存配置
        self.save_config()

        messagebox.showinfo("提示",
                            "配置已保存，将启动后台监控程序。\n\n程序将在后台运行，不会显示窗口。\n查看日志文件了解运行状态。")

        # 启动后台程序
        try:
            import subprocess

            if getattr(sys, 'frozen', False):
                # 如果是打包的exe，直接启动自己
                subprocess.Popen([sys.executable],
                                 creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                # 如果是Python脚本，使用pythonw.exe启动
                pythonw_path = sys.executable.replace('python.exe', 'pythonw.exe')
                script_path = os.path.join(os.path.dirname(__file__), 'main_hidden.py')
                subprocess.Popen([pythonw_path, script_path],
                                 creationflags=subprocess.CREATE_NO_WINDOW)

            self.root.destroy()

        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {str(e)}")

    def run(self):
        """运行界面"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ConfigGUI()
    app.run()