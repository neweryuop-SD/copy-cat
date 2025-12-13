import os
import time
import json
from datetime import datetime

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("警告: psutil 模块未安装，使用备用方法检测U盘")
    print("请运行: pip install psutil")

try:
    import win32api
    import win32file
    import win32con

    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    print("警告: pywin32 模块未安装，使用备用方法检测U盘")
    print("请运行: pip install pywin32")


class USBMoniTor:
    def __init__(self, config, logger, file_handler):
        self.config = config
        self.logger = logger
        self.file_handler = file_handler
        self.detected_drives = set()
        self.exclude_drives = config.get_exclude_drives()
        self.usb_history = set()

    def get_drive_info(self, drive_letter):
        """获取驱动器信息"""
        if HAS_WIN32:
            try:
                drive_name = win32api.GetVolumeInformation(f"{drive_letter}\\")[0]
                if not drive_name:
                    drive_name = "未命名"
                return drive_name
            except:
                return "未知"
        return "未知"

    def is_removable_drive(self, drive_letter):
        """检查是否为可移动驱动器"""
        if HAS_WIN32:
            try:
                drive_type = win32file.GetDriveType(f"{drive_letter}\\")
                return drive_type == win32con.DRIVE_REMOVABLE
            except:
                pass

        if HAS_PSUTIL:
            try:
                for part in psutil.disk_partitions():
                    if part.device.startswith(drive_letter):
                        return 'removable' in part.opts.lower()
            except:
                pass

        # 备用方法：检查是否是A-Z驱动器且不是系统盘
        drive_char = drive_letter[0].upper()
        if drive_char in self.exclude_drives:
            return False

        # 简单检查：路径是否存在并且看起来像可移动驱动器
        if os.path.exists(drive_letter + "\\"):
            # 检查是否有典型的U盘目录结构
            return True

        return False

    def get_all_drives(self):
        """获取所有可用的驱动器"""
        drives = []

        if HAS_PSUTIL:
            try:
                for part in psutil.disk_partitions():
                    drive_letter = part.device[:2]  # 获取驱动器号，如 "C:"
                    if drive_letter and drive_letter[0] not in self.exclude_drives:
                        drives.append(drive_letter)
            except:
                pass
        else:
            # 备用方法：检查所有可能的驱动器
            import string
            for drive_letter in string.ascii_uppercase:
                drive = f"{drive_letter}:"
                if os.path.exists(drive + "\\"):
                    if drive_letter not in self.exclude_drives:
                        drives.append(drive)

        return list(set(drives))

    def check_new_drives(self):
        """检查新插入的驱动器"""
        try:
            current_drives = set(self.get_all_drives())
            new_drives = current_drives - self.detected_drives

            for drive in new_drives:
                if self.is_removable_drive(drive):
                    drive_name = self.get_drive_info(drive)
                    self.logger.log_usb_insert(drive, drive_name)

                    # 记录到历史文件
                    self.record_usb_drive(drive, drive_name)

                    # 复制文件
                    copied_files = self.file_handler.copy_files_from_usb(drive)
                    if copied_files:
                        self.logger.log_info(f"从 {drive} 复制了 {len(copied_files)} 个文件")

            self.detected_drives = current_drives
            return len(new_drives) > 0

        except Exception as e:
            self.logger.log_error(f"检查驱动器失败: {str(e)}")
            return False

    def record_usb_drive(self, drive_letter, drive_name=""):
        """记录U盘驱动器信息"""
        try:
            record_file = os.path.join(self.config.get_target_folder(), "usb_history.txt")
            os.makedirs(os.path.dirname(record_file), exist_ok=True)

            with open(record_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} - 驱动器: {drive_letter} - 名称: {drive_name}\n")
        except Exception as e:
            self.logger.log_error(f"记录U盘信息失败: {str(e)}")

    def start_monitoring(self):
        """开始监控"""
        self.logger.log_info("USB监控程序启动")
        self.detected_drives = set(self.get_all_drives())

        try:
            while True:
                self.check_new_drives()
                time.sleep(self.config.get_check_interval())
        except KeyboardInterrupt:
            self.logger.log_info("监控程序被用户中断")
        except Exception as e:
            self.logger.log_error(f"监控过程中发生错误: {str(e)}")