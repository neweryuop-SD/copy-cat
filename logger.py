import logging
import logging.handlers
from datetime import datetime
import os
import hashlib


class SecureLogger:
    def __init__(self, config):
        self.config = config
        self.log_file = self.secure_log_path(config.get_log_file())
        self.setup_logger()

        # 记录启动日志
        self.log_startup_info()

    def secure_log_path(self, log_file):
        """确保日志文件路径安全"""
        # 防止日志文件被放置在系统目录
        abs_path = os.path.abspath(log_file)
        user_home = os.path.expanduser('~')

        if not abs_path.startswith(user_home):
            # 如果不在用户目录，移动到用户目录
            safe_path = os.path.join(user_home, 'USBMonitor', 'logs', 'usb_monitor.log')
            os.makedirs(os.path.dirname(safe_path), exist_ok=True)
            return safe_path

        return log_file

    def setup_logger(self):
        """配置安全的日志系统"""
        # 创建logger
        self.logger = logging.getLogger('SecureUSBMonitor')
        self.logger.setLevel(logging.DEBUG)

        # 防止重复添加handler
        if self.logger.handlers:
            return

        # 文件handler - 加密日志文件名（可选）
        secure_log_file = self.get_secure_log_filename()

        file_handler = logging.handlers.RotatingFileHandler(
            secure_log_file,
            maxBytes=self.config.config['Logging'].getint('max_log_size') * 1024 * 1024,
            backupCount=self.config.config['Logging'].getint('backup_count'),
            encoding='utf-8'
        )

        # 控制台handler（调试时使用）
        console_handler = logging.StreamHandler()

        # 安全日志格式（不包含敏感信息）
        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 设置日志级别
        log_level = self.config.config['Logging'].get('log_level', 'INFO')
        file_handler.setLevel(getattr(logging, log_level))
        console_handler.setLevel(logging.WARNING)  # 控制台只显示警告和错误

        # 添加handler
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_secure_log_filename(self):
        """获取安全的日志文件名（避免被轻易发现）"""
        # 可以使用简单的文件名混淆
        log_dir = os.path.dirname(self.log_file)
        log_filename = os.path.basename(self.log_file)

        # 对文件名进行简单混淆
        if self.config.config['Security'].getboolean('obfuscate_log_name', False):
            timestamp = datetime.now().strftime("%Y%m")
            hash_name = hashlib.md5(f"usb_log_{timestamp}".encode()).hexdigest()[:8]
            secure_name = f"system_{hash_name}.log"
            return os.path.join(log_dir, secure_name)

        return self.log_file

    def log_startup_info(self):
        """记录启动信息（不包含敏感信息）"""
        import platform
        import getpass

        # 记录基本系统信息（不包含用户名）
        system_info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }

        self.logger.info(f"程序启动 - 系统信息: {system_info}")
        self.logger.info(f"配置文件: {self.config.config_file}")
        self.logger.info(f"目标文件夹: {self.config.get_target_folder()}")
        self.logger.info(f"关键词: {self.config.get_keywords()}")

    def sanitize_message(self, message):
        """清理日志消息中的敏感信息"""
        # 移除可能的密码、密钥等敏感信息
        sensitive_patterns = [
            r'password[=:]\s*\S+',
            r'api[_-]?key[=:]\s*\S+',
            r'token[=:]\s*\S+',
            r'secret[=:]\s*\S+',
        ]

        import re
        for pattern in sensitive_patterns:
            message = re.sub(pattern, '[REDACTED]', message, flags=re.IGNORECASE)

        return message

    def log_usb_insert(self, drive_letter, drive_name=""):
        """记录U盘插入（安全版本）"""
        message = f"USB设备插入 - 驱动器: {drive_letter}"
        if drive_name and drive_name != "未知":
            message += f" - 标签: {drive_name[:20]}"  # 限制标签长度

        safe_message = self.sanitize_message(message)
        self.logger.info(safe_message)

    def log_file_copy(self, source, destination, success=True):
        """记录文件复制（安全版本）"""
        # 只记录文件名，不包含完整路径（可选）
        source_file = os.path.basename(source)
        dest_file = os.path.basename(destination)

        status = "成功" if success else "失败"
        message = f"文件复制{status}: {source_file} -> {dest_file}"

        self.logger.info(message)

    def log_error(self, message):
        """记录错误"""
        safe_message = self.sanitize_message(message)
        self.logger.error(safe_message)

    def log_warning(self, message):
        """记录警告"""
        safe_message = self.sanitize_message(message)
        self.logger.warning(safe_message)

    def log_info(self, message):
        """记录信息"""
        safe_message = self.sanitize_message(message)
        self.logger.info(safe_message)

    def log_debug(self, message):
        """记录调试信息"""
        safe_message = self.sanitize_message(message)
        self.logger.debug(safe_message)