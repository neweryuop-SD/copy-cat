import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
import magic  # 需要安装python-magic-bin


class FileHandler:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.target_folder = config.get_target_folder()
        self.keywords = config.get_keywords()
        self.max_file_size = config.get_max_file_size() * 1024 * 1024

        # 初始化文件类型检测
        try:
            self.magic = magic.Magic(mime=True)
        except:
            self.magic = None
            self.logger.log_warning("文件类型检测不可用，将仅使用扩展名验证")

    def calculate_file_hash(self, file_path):
        """计算文件哈希值，用于去重"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return None

    def is_safe_file_type(self, file_path):
        """检查文件是否为安全类型"""
        try:
            # 使用python-magic检测真实文件类型
            if self.magic:
                mime_type = self.magic.from_file(file_path)
                dangerous_mime_types = [
                    'application/x-msdownload',  # exe
                    'application/x-msdos-program',
                    'application/x-executable',
                    'text/vbscript',
                    'application/x-javascript',
                    'application/x-powershell'
                ]

                if any(dangerous in mime_type for dangerous in dangerous_mime_types):
                    self.logger.log_warning(f"检测到潜在危险文件类型: {file_path} ({mime_type})")
                    return False

            # 检查扩展名
            file_ext = os.path.splitext(file_path)[1].lower()
            dangerous_extensions = ['.exe', '.bat', '.cmd', '.vbs', '.js', '.ps1', '.scr']

            if file_ext in dangerous_extensions:
                self.logger.log_warning(f"检测到危险文件扩展名: {file_path}")
                return False

            return True

        except Exception as e:
            self.logger.log_error(f"文件类型检测失败 {file_path}: {str(e)}")
            return True  # 默认允许

    def sanitize_filename(self, filename):
        """清理文件名，移除危险字符"""
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')

        # 限制文件名长度
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext

        return filename

    def validate_file_path(self, file_path):
        """验证文件路径是否安全"""
        # 检查绝对路径是否安全
        abs_path = os.path.abspath(file_path)

        # 防止路径遍历
        if '..' in abs_path:
            self.logger.log_warning(f"检测到路径遍历尝试: {file_path}")
            return False

        # 检查路径是否在安全白名单中
        if not self.config.is_safe_path(os.path.dirname(abs_path)):
            self.logger.log_warning(f"文件路径不在安全白名单中: {file_path}")
            return False

        return True

    def should_copy_file(self, file_path):
        """检查文件是否需要复制，增加安全检查"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False

            # 检查文件大小
            if os.path.getsize(file_path) > self.max_file_size:
                self.logger.log_debug(f"文件过大跳过: {file_path}")
                return False

            # 检查文件类型安全性
            if not self.is_safe_file_type(file_path):
                self.logger.log_warning(f"不安全文件类型被阻止: {file_path}")
                return False

            # 检查路径安全性
            if not self.validate_file_path(file_path):
                return False

            # 检查文件扩展名
            file_ext = os.path.splitext(file_path)[1].lower()
            return any(keyword.lower() in file_ext for keyword in self.keywords)

        except Exception as e:
            self.logger.log_error(f"文件检查失败 {file_path}: {str(e)}")
            return False

    def copy_files_from_usb(self, usb_drive):
        """从U盘复制文件，增加安全检查"""
        try:
            # 验证U盘路径
            if not os.path.exists(usb_drive):
                self.logger.log_error(f"U盘路径不存在: {usb_drive}")
                return []

            # 创建目标子文件夹
            current_date = datetime.now().strftime("%Y-%m-%d")
            drive_name = self.sanitize_filename(os.path.basename(usb_drive.rstrip('\\')))

            # 使用安全的目标文件夹结构
            target_subfolder = os.path.join(
                self.target_folder,
                current_date,
                drive_name
            )

            # 确保目标路径安全
            if not target_subfolder.startswith(self.target_folder):
                self.logger.log_error(f"目标路径不安全: {target_subfolder}")
                return []

            os.makedirs(target_subfolder, exist_ok=True)

            copied_files = []
            file_hashes = set()  # 用于去重

            # 限制遍历深度
            max_depth = 5
            current_depth = 0

            def safe_walk(root, depth):
                """安全的目录遍历"""
                if depth > max_depth:
                    return [], []

                try:
                    dirs = []
                    files = []

                    for item in os.listdir(root):
                        item_path = os.path.join(root, item)

                        if os.path.isdir(item_path):
                            dirs.append(item)
                        else:
                            files.append(item)

                    return dirs, files
                except PermissionError:
                    self.logger.log_warning(f"无权访问目录: {root}")
                    return [], []
                except Exception as e:
                    self.logger.log_error(f"遍历目录失败 {root}: {str(e)}")
                    return [], []

            # 遍历U盘文件（使用安全的遍历方式）
            stack = [(usb_drive, 0)]
            while stack:
                root, depth = stack.pop()

                dirs, files = safe_walk(root, depth)

                # 处理文件
                for file in files:
                    source_file = os.path.join(root, file)

                    if self.should_copy_file(source_file):
                        # 计算文件哈希用于去重
                        file_hash = self.calculate_file_hash(source_file)
                        if file_hash and file_hash in file_hashes:
                            self.logger.log_debug(f"重复文件跳过: {source_file}")
                            continue

                        if file_hash:
                            file_hashes.add(file_hash)

                        # 保持相对路径结构
                        rel_path = os.path.relpath(root, usb_drive)
                        if rel_path == '.':
                            dest_folder = target_subfolder
                        else:
                            # 清理路径组件
                            safe_rel_path = self.sanitize_filename(rel_path)
                            dest_folder = os.path.join(target_subfolder, safe_rel_path)

                        # 创建目标文件夹
                        os.makedirs(dest_folder, exist_ok=True)

                        # 清理文件名
                        safe_filename = self.sanitize_filename(file)
                        dest_file = os.path.join(dest_folder, safe_filename)

                        # 获取唯一文件名
                        dest_file = self.get_unique_filename(dest_file)

                        # 复制文件
                        try:
                            shutil.copy2(source_file, dest_file)

                            # 验证复制后的文件
                            if os.path.exists(dest_file) and \
                                    os.path.getsize(source_file) == os.path.getsize(dest_file):

                                copied_files.append({
                                    'source': source_file,
                                    'destination': dest_file,
                                    'size': os.path.getsize(source_file)
                                })
                                self.logger.log_file_copy(source_file, dest_file, True)
                            else:
                                self.logger.log_error(f"文件复制验证失败: {source_file}")

                        except Exception as e:
                            self.logger.log_error(f"复制文件失败 {source_file}: {str(e)}")

                # 添加子目录到栈中
                if depth < max_depth:
                    for dir_name in dirs:
                        dir_path = os.path.join(root, dir_name)
                        stack.append((dir_path, depth + 1))

            self.logger.log_info(f"从 {usb_drive} 复制了 {len(copied_files)} 个文件")
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