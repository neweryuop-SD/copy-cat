#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
copy-cat - 一键打包脚本
支持自定义图标打包
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


class CopyCatBuilder:
    def __init__(self):
        self.project_name = "copy-cat"
        self.version = "2.0"
        self.author = "LYJY"

        # 需要打包的文件列表
        self.source_files = [
            'main_hidden.py',  # 后台主程序
            'config.py',  # 配置模块
            'logger.py',  # 日志模块
            'file_handler.py',  # 文件处理模块
            'monitor.py',  # 监控模块
            'config_gui.py',  # 配置界面
            'service_manager.py',  # 服务管理器
            'config.ini',  # 配置文件
            'README.md',  # 说明文档
        ]

        # 检查文件是否存在
        self.missing_files = []
        for file in self.source_files:
            if not os.path.exists(file):
                self.missing_files.append(file)

    def check_dependencies(self):
        """检查打包依赖"""
        print("检查打包依赖...")
        print("-" * 50)

        dependencies = {
            'PyInstaller': 'pyinstaller',
            'psutil': 'psutil',
            'pywin32': 'pywin32',
        }

        missing = []
        for name, package in dependencies.items():
            try:
                __import__(package.replace('-', '_'))
                print(f"✓ {name} 已安装")
            except ImportError:
                print(f"✗ {name} 未安装")
                missing.append(package)

        if missing:
            print(f"\n缺少依赖包: {', '.join(missing)}")
            install = input("是否现在安装? (y/n): ")
            if install.lower() == 'y':
                for package in missing:
                    print(f"正在安装 {package}...")
                    result = subprocess.run([sys.executable, "-m", "pip", "install", package],
                                            capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"赞美欧姆尼塞娅吧 ✓ {package} 安装成功")
                    else:
                        print(f"叫程序员麻溜过来修BUG ✗ {package} 安装失败: {result.stderr}")
            else:
                print("请手动安装依赖:")
                print(f"pip install {' '.join(missing)}")
                return False

        print("\n赞美欧姆尼塞娅吧 所有依赖已满足！")
        return True

    def clean_previous_builds(self):
        """清理之前的构建文件"""
        print("\n清理之前的构建文件...")

        dirs_to_remove = ['build', 'dist', '__pycache__']
        files_to_remove = [f'{self.project_name}.spec', 'main_hidden.spec', 'config_gui.spec']

        for dir_name in dirs_to_remove:
            if os.path.exists(dir_name):
                try:
                    shutil.rmtree(dir_name)
                    print(f"赞美欧姆尼塞娅吧 ✓ 已删除目录: {dir_name}")
                except Exception as e:
                    print(f"叫程序员麻溜过来修BUG ✗ 删除目录失败 {dir_name}: {e}")

        for file_name in files_to_remove:
            if os.path.exists(file_name):
                try:
                    os.remove(file_name)
                    print(f"赞美欧姆尼塞娅吧 ✓ 已删除文件: {file_name}")
                except Exception as e:
                    print(f"叫程序员麻溜过来修BUG ✗ 删除文件失败 {file_name}: {e}")

        print("清理完成！")

    def get_custom_icon(self):
        """获取自定义图标"""
        # 支持的图标文件名列表
        icon_files = [
            'copy-cat.ico',  # 首选图标名
            'icon.ico',  # 通用图标名
            'app.ico',  # 应用图标名
            'custom.ico',  # 自定义图标名
        ]

        # 检查是否存在自定义图标
        for icon_file in icon_files:
            if os.path.exists(icon_file):
                print(f"赞美欧姆尼塞娅吧 ✓ 发现图标文件: {icon_file}")
                return icon_file

        print("ℹ 未发现图标文件，将使用默认图标或跳过图标设置")
        return None

    def create_default_icon(self):
        """创建默认图标（如果不存在自定义图标）"""
        print("正在创建默认图标...")

        try:
            from PIL import Image, ImageDraw, ImageFont

            # 创建图标
            sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
            images = []

            for size in sizes:
                img = Image.new('RGBA', size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(img)

                # 绘制图标背景
                width, height = size
                margin = width // 10

                # 圆形背景
                draw.ellipse([margin, margin, width - margin, height - margin],
                             fill=(70, 130, 180), outline=(47, 79, 79), width=3)

                # 绘制猫头
                if width >= 64:  # 大图标才绘制详细图案
                    # 耳朵
                    draw.polygon([
                        (width // 2 - width // 4, height // 3),
                        (width // 2 - width // 6, height // 4),
                        (width // 2 - width // 12, height // 3)
                    ], fill=(47, 79, 79))

                    draw.polygon([
                        (width // 2 + width // 12, height // 3),
                        (width // 2 + width // 6, height // 4),
                        (width // 2 + width // 4, height // 3)
                    ], fill=(47, 79, 79))

                    # 眼睛
                    eye_radius = width // 10
                    left_eye_x = width // 2 - width // 6
                    right_eye_x = width // 2 + width // 6
                    eye_y = height // 2 - height // 10

                    draw.ellipse([left_eye_x - eye_radius, eye_y - eye_radius,
                                  left_eye_x + eye_radius, eye_y + eye_radius],
                                 fill=(255, 255, 255))
                    draw.ellipse([right_eye_x - eye_radius, eye_y - eye_radius,
                                  right_eye_x + eye_radius, eye_y + eye_radius],
                                 fill=(255, 255, 255))

                    # 瞳孔
                    pupil_radius = eye_radius // 2
                    draw.ellipse([left_eye_x - pupil_radius, eye_y - pupil_radius,
                                  left_eye_x + pupil_radius, eye_y + pupil_radius],
                                 fill=(0, 0, 0))
                    draw.ellipse([right_eye_x - pupil_radius, eye_y - pupil_radius,
                                  right_eye_x + pupil_radius, eye_y + pupil_radius],
                                 fill=(0, 0, 0))

                    # 鼻子
                    nose_y = eye_y + height // 10
                    draw.polygon([
                        (width // 2 - width // 20, nose_y),
                        (width // 2 + width // 20, nose_y),
                        (width // 2, nose_y + height // 20)
                    ], fill=(255, 105, 180))

                    # 胡须
                    whisker_length = width // 4
                    whisker_y = nose_y
                    draw.line([(width // 2 - whisker_length, whisker_y),
                               (width // 2 - width // 20, whisker_y)],
                              fill=(47, 79, 79), width=2)
                    draw.line([(width // 2 + width // 20, whisker_y),
                               (width // 2 + whisker_length, whisker_y)],
                              fill=(47, 79, 79), width=2)

                    # 嘴巴
                    mouth_y = nose_y + height // 15
                    draw.arc([width // 2 - width // 8, mouth_y - height // 30,
                              width // 2 + width // 8, mouth_y + height // 30],
                             0, -180, fill=(47, 79, 79), width=2)

                else:  # 小图标简化设计
                    # 简单猫脸
                    face_radius = width // 2 - margin
                    draw.ellipse([margin * 2, margin * 2, width - margin * 2, height - margin * 2],
                                 fill=(70, 130, 180))

                    # 简单眼睛
                    eye_size = face_radius // 3
                    draw.ellipse([width // 2 - eye_size, height // 2 - eye_size,
                                  width // 2 - eye_size // 2, height // 2 - eye_size // 2],
                                 fill=(255, 255, 255))
                    draw.ellipse([width // 2 + eye_size // 2, height // 2 - eye_size,
                                  width // 2 + eye_size, height // 2 - eye_size // 2],
                                 fill=(255, 255, 255))

                images.append(img)

            # 保存为ICO
            default_icon = 'default_icon.ico'
            images[0].save(default_icon, format='ICO', sizes=[(size[0], size[1]) for size in sizes])
            print(f"赞美欧姆尼塞娅吧 ✓ 默认图标已创建: {default_icon}")
            return default_icon

        except ImportError:
            print("✗ 需要Pillow库来创建图标，跳过图标创建")
            print("  请运行: pip install Pillow")
            return None
        except Exception as e:
            print(f"叫程序员麻溜过来修BUG ✗ 创建图标失败: {e}")
            return None

    def build_main_exe(self, icon_file=None):
        """构建主程序EXE（后台无窗口版本）"""
        print("\n" + "=" * 50)
        print("构建主程序EXE（后台无窗口版本）")
        print("=" * 50)

        # PyInstaller命令
        cmd = [
            'pyinstaller',
            f'--name={self.project_name}',
            '--onefile',  # 单个EXE文件
            '--windowed',  # 无控制台窗口
            '--clean',
            '--noconfirm',
            '--add-data=config.ini;.',  # 包含配置文件
            '--hidden-import=win32timezone',
            '--hidden-import=configparser',
            '--hidden-import=logging.handlers',
            '--hidden-import=psutil',
            '--hidden-import=psutil._psutil_windows',
            '--exclude-module=tkinter',  # 排除tkinter（后台版不需要）
        ]

        # 添加图标
        if icon_file and os.path.exists(icon_file):
            cmd.append(f'--icon={icon_file}')
            print(f"使用图标: {icon_file}")

        cmd.append('main_hidden.py')

        # 执行命令
        print("正在构建...")
        result = subprocess.run(' '.join(cmd), shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print("赞美欧姆尼塞娅吧 ✓ 主程序EXE构建成功！")

            # 复制配置文件到dist目录
            if os.path.exists('config.ini'):
                shutil.copy2('config.ini', 'dist/')
                print("✓ 已复制配置文件")

            # 检查文件大小
            exe_path = f'dist/{self.project_name}.exe'
            if os.path.exists(exe_path):
                size = os.path.getsize(exe_path) / 1024 / 1024
                print(f"文件大小: {size:.2f} MB")

            return True
        else:
            print("叫程序员麻溜过来修BUG ✗ EXE构建失败")
            if result.stderr:
                print("错误信息:", result.stderr)
            return False

    def build_gui_exe(self, icon_file=None):
        """构建配置界面EXE"""
        print("\n" + "=" * 50)
        print("构建配置界面EXE")
        print("=" * 50)

        cmd = [
            'pyinstaller',
            f'--name={self.project_name}_GUI',
            '--onefile',
            '--windowed',
            '--clean',
            '--noconfirm',
            '--add-data=config.ini;.',
            '--hidden-import=tkinter',
            '--hidden-import=configparser',
        ]

        # 添加图标
        if icon_file and os.path.exists(icon_file):
            cmd.append(f'--icon={icon_file}')
            print(f"使用图标: {icon_file}")

        cmd.append('config_gui.py')

        print("正在构建...")
        result = subprocess.run(' '.join(cmd), shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print("赞美欧姆尼塞娅吧 ✓ 配置界面EXE构建成功！")
            return True
        else:
            print("叫程序员麻溜过来修BUG ✗ 配置界面EXE构建失败")
            if result.stderr:
                print("错误信息:", result.stderr)
            return False

    def build_manager_exe(self, icon_file=None):
        """构建服务管理器EXE"""
        print("\n" + "=" * 50)
        print("构建服务管理器EXE")
        print("=" * 50)

        cmd = [
            'pyinstaller',
            f'--name={self.project_name}_Manager',
            '--onedir',  # 目录结构（包含更多文件）
            '--console',  # 有控制台（方便管理）
            '--clean',
            '--noconfirm',
            '--add-data=config.ini;.',
            '--hidden-import=psutil',
            '--hidden-import=win32api',
        ]

        # 添加图标
        if icon_file and os.path.exists(icon_file):
            cmd.append(f'--icon={icon_file}')
            print(f"使用图标: {icon_file}")

        cmd.append('service_manager.py')

        print("别催了！没看见正在构建吗...")
        result = subprocess.run(' '.join(cmd), shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print("赞美欧姆尼塞娅吧 ✓ 服务管理器EXE构建成功！")
            return True
        else:
            print("叫程序员麻溜过来修BUG ✗ 服务管理器EXE构建失败")
            if result.stderr:
                print("错误信息:", result.stderr)
            return False

    def build_all_exe(self):
        """一键构建所有EXE文件"""
        print("\n" + "=" * 50)
        print("一键构建所有EXE文件（懒人方式）")
        print("=" * 50)

        # 获取图标
        icon_file = self.get_custom_icon()
        if not icon_file:
            icon_file = self.create_default_icon()

        # 清理之前的构建
        self.clean_previous_builds()

        # 构建主程序
        success1 = self.build_main_exe(icon_file)

        # 构建GUI程序
        success2 = self.build_gui_exe(icon_file)

        # 构建管理器程序
        success3 = self.build_manager_exe(icon_file)

        if success1 and success2 and success3:
            print("\n✓ 所有EXE文件构建完成！")
            print(f"\n文件位置: dist/ 目录")
            print(f"1. {self.project_name}.exe        - 主程序（后台运行）")
            print(f"2. {self.project_name}_GUI.exe    - 配置界面")
            print(f"3. {self.project_name}_Manager.exe - 服务管理器")

            # 创建使用说明
            self.create_readme()

            return True
        else:
            print("\n✗ 部分EXE构建失败")
            return False

    def create_installer(self):
        """创建安装程序"""
        print("\n" + "=" * 50)
        print("创建安装程序")
        print("=" * 50)

        # 检查Inno Setup
        inno_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
            r"C:\Program Files\Inno Setup 5\ISCC.exe",
        ]

        compiler = None
        for path in inno_paths:
            if os.path.exists(path):
                compiler = path
                break

        if not compiler:
            print("ℹ 未找到Inno Setup，我选择跳过安装程序创建")
            print("  你需要从 https://jrsoftware.org/isdl.php 下载Inno Setup")
            return False

        # 获取图标
        icon_file = self.get_custom_icon()
        if not icon_file:
            icon_file = self.create_default_icon()

        # 先构建所有EXE
        if not self.build_all_exe():
            print("✗ EXE构建失败，无法创建安装程序，快叫程序员过来修！")
            return False

        # 创建安装脚本
        iss_content = f"""; copy-cat安装脚本

#define MyAppName "copy-cat"
#define MyAppVersion "{self.version}"
#define MyAppPublisher "{self.author}"
#define MyAppURL "https://example.com"
#define MyAppExeName "{self.project_name}.exe"
#define MyAppGUID "{{{{copy-cat-{self.version.replace('.', '-')}}}}}

[Setup]
AppId={{{{MyAppGUID}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=README.txt
OutputDir=Installer
OutputBaseFilename={self.project_name}_Setup
SetupIconFile={icon_file}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
DisableWelcomePage=no
DisableProgramGroupPage=yes

[Languages]
Name: "chinese"; MessagesFile: "compiler:Languages\\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加快捷方式:"
Name: "startup"; Description: "开机自动启动"; GroupDescription: "Windows启动:"

[Files]
Source: "dist\\{self.project_name}.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "dist\\{self.project_name}_GUI.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "dist\\{self.project_name}_Manager\\*"; DestDir: "{{app}}\\Manager"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "config.ini"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\copy-cat (后台)"; Filename: "{{app}}\\{self.project_name}.exe"
Name: "{{group}}\\copy-cat 配置界面"; Filename: "{{app}}\\{self.project_name}_GUI.exe"
Name: "{{group}}\\copy-cat 服务管理"; Filename: "{{app}}\\Manager\\{self.project_name}_Manager.exe"
Name: "{{group}}\\卸载copy-cat"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\copy-cat"; Filename: "{{app}}\\{self.project_name}.exe"; Tasks: desktopicon
Name: "{{userstartup}}\\copy-cat"; Filename: "{{app}}\\{self.project_name}.exe"; Tasks: startup

[Run]
Filename: "{{app}}\\{self.project_name}.exe"; Description: "启动copy-cat程序"; Flags: nowait postinstall skipifsilent
Filename: "{{app}}\\{self.project_name}_GUI.exe"; Description: "打开配置界面"; Flags: nowait unchecked

[UninstallRun]
Filename: "{{app}}\\{self.project_name}.exe"; Parameters: "uninstall"; RunOnceId: "UninstallCopyCat"
"""

        # 保存安装脚本
        with open('setup.iss', 'w', encoding='utf-8') as f:
            f.write(iss_content)

        print("✓ 安装脚本已创建: setup.iss")

        # 创建说明文件
        with open('README.txt', 'w', encoding='utf-8') as f:
            f.write(f"""copy-cat v{self.version}

这是一个后台运行的USB文件监控程序，具有以下功能：

1. 监控U盘插入
2. 自动备份指定类型的文件
3. 后台无窗口运行
4. 开机自启动
5. 详细日志记录

使用说明：
1. 安装后，程序会自动添加到开机启动
2. 程序在后台运行，无任何界面
3. 使用"copy-cat服务管理"程序管理服务
4. 使用"copy-cat配置界面"修改配置

隐私声明：
本程序仅备份用户指定的文件类型，所有文件保存在本地，
不会上传到任何服务器，不会收集用户隐私信息。

技术支持：
如有问题，请查看日志文件或联系开发者。
""")

        # 创建许可文件
        with open('LICENSE.txt', 'w', encoding='utf-8') as f:
            f.write("""copy-cat - 使用许可

1. 本程序仅供合法的USB文件备份目的使用
2. 禁止用于非法监控或侵犯他人隐私
3. 使用者需遵守当地法律法规
4. 程序作者不承担任何滥用责任

版权所有 (c) 2025 LYJY
""")

        # 编译安装程序
        print("正在编译安装程序...")
        result = subprocess.run([compiler, 'setup.iss'], capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ 安装程序创建成功！")
            print(f"安装程序位置: Installer\\{self.project_name}_Setup.exe")
            return True
        else:
            print("✗ 编译安装程序失败")
            if result.stderr:
                print("错误信息:", result.stderr)
            return False

    def create_readme(self):
        """创建使用说明"""
        print("\n创建使用说明...")

        readme_content = f"""copy-cat v{self.version}
============================

程序文件说明：
1. {self.project_name}.exe           - 主程序（后台无窗口运行）
2. {self.project_name}_GUI.exe       - 配置界面（图形界面）
3. {self.project_name}_Manager.exe   - 服务管理器（命令行管理）
4. config.ini                       - 配置文件

使用方法：
1. 直接运行 {self.project_name}.exe
   - 程序在后台运行，无任何窗口
   - 自动监控U盘插入并备份文件
   - 所有日志记录到文件

2. 开机自启动：
   - 运行: {self.project_name}.exe install
   - 或使用服务管理器安装

3. 配置程序：
   - 运行 {self.project_name}_GUI.exe
   - 修改配置文件 config.ini

4. 管理服务：
   - 运行 {self.project_name}_Manager.exe
   - 支持启动、停止、安装、卸载等操作

配置文件 (config.ini)：
[Settings]
keywords = .doc,.docx,.pdf,.txt,.xlsx,.xls,.pptx,.ppt,.jpg,.png
target_folder = C:\\copy-cat_backup
check_interval = 5

[Security]
max_file_size = 100
exclude_drives = C

日志文件：
1. copy_cat_service.log  - 服务运行日志
2. copy_cat_status.log   - 状态日志
3. service_error.log     - 错误日志
4. copy-cat.log          - 监控日志

技术支持：
- 查看日志文件了解程序运行状态
- 修改配置文件调整程序行为
- 使用服务管理器管理程序

安全声明：
本程序仅用于合法的USB文件备份目的，
使用者需遵守相关法律法规，尊重他人隐私。
"""

        with open(f'dist/{self.project_name}使用说明.txt', 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f"✓ 使用说明已创建: dist/{self.project_name}使用说明.txt")

    def show_menu(self):
        """显示打包菜单"""
        while True:
            print("\n" + "=" * 60)
            print(f"{self.project_name} - 打包工具")
            print("=" * 60)
            print(f"版本: {self.version}")
            print(f"作者: {self.author}")

            # 检查自定义图标
            icon_file = self.get_custom_icon()
            if icon_file:
                print(f"图标: {icon_file}")
            else:
                print("没有自定义图片啊！")

            if self.missing_files:
                print(f"\n警告: 缺 {len(self.missing_files)} 个文件")
                for file in self.missing_files:
                    print(f"  - {file}")

            print("\n选择打包选项:")
            print("1. 检查依赖")
            print("2. 清理构建文件")
            print("3. 使用自定义图标打包")
            print("4. 创建默认图标并打包")
            print("5. 构建主程序EXE (后台版)")
            print("6. 构建配置界面EXE")
            print("7. 构建服务管理器EXE")
            print("8. 一键构建所有EXE")
            print("9. 创建安装程序 (需要Inno Setup)")
            print("10. 创建使用说明")
            print("0. 退出")

            try:
                choice = input("\n请选择 (0-10): ").strip()

                if choice == '1':
                    self.check_dependencies()
                elif choice == '2':
                    self.clean_previous_builds()
                elif choice == '3':
                    icon_file = self.get_custom_icon()
                    if icon_file:
                        print(f"使用自定义图标: {icon_file}")
                        self.build_all_exe()
                    else:
                        print("LOOK MY EYES!!!图标在哪？")
                elif choice == '4':
                    icon_file = self.create_default_icon()
                    if icon_file:
                        self.build_all_exe()
                elif choice == '5':
                    icon_file = self.get_custom_icon()
                    if not icon_file:
                        icon_file = self.create_default_icon()
                    self.build_main_exe(icon_file)
                elif choice == '6':
                    icon_file = self.get_custom_icon()
                    if not icon_file:
                        icon_file = self.create_default_icon()
                    self.build_gui_exe(icon_file)
                elif choice == '7':
                    icon_file = self.get_custom_icon()
                    if not icon_file:
                        icon_file = self.create_default_icon()
                    self.build_manager_exe(icon_file)
                elif choice == '8':
                    self.build_all_exe()
                elif choice == '9':
                    self.create_installer()
                elif choice == '10':
                    self.create_readme()
                elif choice == '0':
                    print("退出打包工具")
                    break
                else:
                    print("无效选择")

                if choice not in ['0']:
                    input("\n按 Enter 继续...")

            except KeyboardInterrupt:
                print("\n\n用户中断")
                break
            except Exception as e:
                print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    builder = CopyCatBuilder()
    builder.show_menu()