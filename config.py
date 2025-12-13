import configparser
import os
from pathlib import Path
import json


class Config:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.safe_paths = []
        self.load_config()

    def load_config(self):
        """安全加载配置文件"""
        if not os.path.exists(self.config_file):
            self.create_default_config()

        try:
            self.config.read(self.config_file, encoding='utf-8')

            # 验证配置文件完整性
            self.validate_config()

            # 确保目标文件夹在安全位置
            target_folder = self.get_target_folder()
            self.validate_safe_path(target_folder)

            # 创建目标文件夹（如果不存在）
            os.makedirs(target_folder, exist_ok=True)

            # 加载安全路径白名单
            self.load_safe_paths()

        except Exception as e:
            print(f"配置文件错误: {str(e)}")
            self.create_default_config()
            self.config.read(self.config_file, encoding='utf-8')

    def validate_config(self):
        """验证配置文件"""
        required_sections = ['Settings', 'Logging', 'Security']
        for section in required_sections:
            if not self.config.has_section(section):
                raise ValueError(f"配置文件缺少必要部分: {section}")

    def validate_safe_path(self, path):
        """验证路径是否安全"""
        # 防止路径遍历攻击
        if '..' in path or path.startswith('\\') or ':' in path[1:]:
            raise ValueError(f"不安全路径: {path}")

        # 限制到用户目录下
        user_home = os.path.expanduser('~')
        abs_path = os.path.abspath(path)
        user_home = os.path.abspath(user_home)

        # 确保路径在用户目录下
        if not abs_path.startswith(user_home):
            raise ValueError(f"路径必须在用户目录下: {path}")

    def load_safe_paths(self):
        """加载安全路径白名单"""
        safe_paths_file = os.path.join(
            os.path.dirname(self.config_file),
            'safe_paths.json'
        )

        if os.path.exists(safe_paths_file):
            try:
                with open(safe_paths_file, 'r', encoding='utf-8') as f:
                    self.safe_paths = json.load(f)
            except:
                self.safe_paths = []
        else:
            # 默认安全路径
            self.safe_paths = [
                os.path.expanduser('~\\Documents'),
                os.path.expanduser('~\\Desktop'),
                os.path.expanduser('~\\Downloads')
            ]
            self.save_safe_paths()

    def save_safe_paths(self):
        """保存安全路径"""
        safe_paths_file = os.path.join(
            os.path.dirname(self.config_file),
            'safe_paths.json'
        )
        with open(safe_paths_file, 'w', encoding='utf-8') as f:
            json.dump(self.safe_paths, f, ensure_ascii=False, indent=2)

    def is_safe_path(self, path):
        """检查路径是否在安全白名单中"""
        abs_path = os.path.abspath(path)
        for safe_path in self.safe_paths:
            if abs_path.startswith(os.path.abspath(safe_path)):
                return True
        return False

    def get_keywords(self):
        """获取关键词列表，增加安全检查"""
        keywords_str = self.config['Settings'].get('keywords', '')
        keywords = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]

        # 过滤危险文件类型
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.vbs', '.js', '.ps1']
        safe_keywords = [kw for kw in keywords if kw not in dangerous_extensions]

        return safe_keywords

    def get_target_folder(self):
        """获取目标文件夹，确保在用户目录下"""
        default_folder = os.path.join(
            os.path.expanduser('~'),
            'USB_Backup'
        )

        folder = self.config['Settings'].get('target_folder', default_folder)
        folder = os.path.expandvars(folder)

        # 确保路径在用户目录下
        if not folder.startswith(os.path.expanduser('~')):
            folder = default_folder

        return folder

    def get_check_interval(self):
        """获取检查间隔"""
        return int(self.config['Settings'].get('check_interval', '5'))

    def get_log_file(self):
        """获取日志文件路径"""
        return self.config['Logging'].get('log_file', 'usb_monitor.log')

    def get_exclude_drives(self):
        """获取排除的驱动器"""
        drives = self.config['Security'].get('exclude_drives', '')
        return [d.strip().upper() for d in drives.split(',') if d.strip()]

    def get_max_file_size(self):
        """获取最大文件大小(MB)"""
        return int(self.config['Security'].get('max_file_size', '100'))

    def should_log_all_usb(self):
        """是否记录所有U盘"""
        return self.config['Settings'].getboolean('log_all_usb', True)