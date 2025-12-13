import logging
import logging.handlers
import os
from datetime import datetime


class Logger:
    def __init__(self, config):
        self.config = config
        self.setup_logger()

    def setup_logger(self):
        """配置日志系统"""
        log_file = self.get_log_file()

        # 创建logger
        self.logger = logging.getLogger('CopyCat')
        self.logger.setLevel(logging.DEBUG)

        # 防止重复添加handler
        if self.logger.handlers:
            return

        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 文件handler - 按大小轮转
        try:
            max_size = int(self.config.config['Logging'].get('max_log_size', '10')) * 1024 * 1024
            backup_count = int(self.config.config['Logging'].get('backup_count', '5'))

            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
        except:
            # 如果配置读取失败，使用默认配置
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )

        # 控制台handler (用于调试)
        console_handler = logging.StreamHandler()

        # 设置格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 设置日志级别
        try:
            log_level = self.config.config['Logging'].get('log_level', 'INFO')
            file_handler.setLevel(getattr(logging, log_level))
            console_handler.setLevel(logging.INFO)
        except:
            file_handler.setLevel(logging.INFO)
            console_handler.setLevel(logging.INFO)

        # 添加handler
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_log_file(self):
        """获取日志文件路径"""
        return self.config.config['Logging'].get('log_file', 'usb_monitor.log')

    def log_usb_insert(self, drive_letter, drive_name=""):
        """记录U盘插入"""
        message = f"USB插入 - 驱动器: {drive_letter}"
        if drive_name and drive_name != "Unknown":
            message += f" - 名称: {drive_name}"
        self.logger.info(message)

    def log_file_copy(self, source, destination, success=True):
        """记录文件复制"""
        status = "成功" if success else "失败"
        source_name = os.path.basename(source)
        dest_name = os.path.basename(destination)
        self.logger.info(f"文件复制 {status}: {source_name} -> {dest_name}")

    def log_error(self, message):
        """记录错误"""
        self.logger.error(f"错误: {message}")

    def log_warning(self, message):
        """记录警告"""
        self.logger.warning(f"警告: {message}")

    def log_info(self, message):
        """记录信息"""
        self.logger.info(message)

    def log_debug(self, message):
        """记录调试信息"""
        self.logger.debug(message)