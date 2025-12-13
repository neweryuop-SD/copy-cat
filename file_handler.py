import os
import shutil
from datetime import datetime


class FileHandler:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.target_folder = config.get_target_folder()
        self.keywords = config.get_keywords()

        # 获取最大文件大小（转换为字节）
        try:
            max_size_mb = config.get_max_file_size()
            self.max_file_size = max_size_mb * 1024 * 1024
        except:
            self.max_file_size = 100 * 1024 * 1024  # 默认100MB

        # 确保目标文件夹存在
        os.makedirs(self.target_folder, exist_ok=True)

    def should_copy_file(self, file_path):
        """检查文件是否需要复制"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False

            # 检查文件大小
            if os.path.getsize(file_path) > self.max_file_size:
                self.logger.log_info(f"文件过大跳过: {os.path.basename(file_path)}")
                return False

            # 检查文件扩展名
            file_ext = os.path.splitext(file_path)[1].lower()
            for keyword in self.keywords:
                if keyword.lower() in file_ext:
                    return True

            return False

        except Exception as e:
            self.logger.log_error(f"检查文件失败 {file_path}: {str(e)}")
            return False

    def copy_files_from_usb(self, usb_drive):
        """从U盘复制文件"""
        try:
            # 验证U盘路径是否存在
            if not os.path.exists(usb_drive):
                self.logger.log_error(f"U盘路径不存在: {usb_drive}")
                return []

            # 创建目标子文件夹: 日期/USB驱动器名
            current_date = datetime.now().strftime("%Y-%m-%d")
            drive_name = os.path.basename(usb_drive.rstrip('\\'))
            if not drive_name or drive_name.endswith(':'):
                drive_name = f"USB_{usb_drive[0]}"

            target_subfolder = os.path.join(
                self.target_folder,
                current_date,
                drive_name
            )

            # 确保目标路径存在
            os.makedirs(target_subfolder, exist_ok=True)

            copied_files = []

            # 遍历U盘文件
            for root, dirs, files in os.walk(usb_drive):
                # 跳过系统目录
                if 'System Volume Information' in root or '$RECYCLE.BIN' in root:
                    continue

                for file in files:
                    source_file = os.path.join(root, file)

                    if self.should_copy_file(source_file):
                        # 保持相对路径结构
                        rel_path = os.path.relpath(root, usb_drive)
                        if rel_path == '.':
                            dest_folder = target_subfolder
                        else:
                            dest_folder = os.path.join(target_subfolder, rel_path)
                            os.makedirs(dest_folder, exist_ok=True)

                        dest_file = os.path.join(dest_folder, file)

                        # 避免文件名冲突
                        dest_file = self.get_unique_filename(dest_file)

                        # 复制文件
                        try:
                            shutil.copy2(source_file, dest_file)
                            copied_files.append({
                                'source': source_file,
                                'destination': dest_file,
                                'size': os.path.getsize(source_file)
                            })
                            self.logger.log_file_copy(source_file, dest_file, True)
                        except Exception as e:
                            self.logger.log_error(f"复制文件失败 {source_file}: {str(e)}")

            return copied_files

        except Exception as e:
            self.logger.log_error(f"遍历U盘文件失败 {usb_drive}: {str(e)}")
            return []

    def get_unique_filename(self, filepath):
        """获取唯一文件名，避免覆盖"""
        if not os.path.exists(filepath):
            return filepath

        base, ext = os.path.splitext(filepath)
        counter = 1

        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1

        return f"{base}_{counter}{ext}"