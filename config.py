import configparser
import os
from pathlib import Path


class Config:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            self.create_default_config()

        self.config.read(self.config_file, encoding='utf-8')

        # 确保目标文件夹存在
        target_folder = self.get_target_folder()
        os.makedirs(target_folder, exist_ok=True)

    def create_default_config(self):
        """创建默认配置文件"""
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

        print(f"✓ 已创建默认配置文件: {self.config_file}")

    def get_keywords(self):
        """获取关键词列表"""
        keywords_str = self.config['Settings'].get('keywords', '')
        return [kw.strip() for kw in keywords_str.split(',') if kw.strip()]

    def get_target_folder(self):
        """获取目标文件夹"""
        folder = self.config['Settings'].get('target_folder', 'C:\\USB_Backup')
        # 支持环境变量
        folder = os.path.expandvars(folder)
        # 确保路径存在
        os.makedirs(folder, exist_ok=True)
        return folder

    def get_check_interval(self):
        """获取检查间隔"""
        try:
            return int(self.config['Settings'].get('check_interval', '5'))
        except ValueError:
            return 5

    def get_exclude_drives(self):
        """获取排除的驱动器"""
        drives = self.config['Security'].get('exclude_drives', 'C')
        return [d.strip().upper() for d in drives.split(',') if d.strip()]

    def get_max_file_size(self):
        """获取最大文件大小(MB)"""
        try:
            return int(self.config['Security'].get('max_file_size', '100'))
        except ValueError:
            return 100

    def should_log_all_usb(self):
        """是否记录所有U盘"""
        return self.config['Settings'].getboolean('log_all_usb', True)