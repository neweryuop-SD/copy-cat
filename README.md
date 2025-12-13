# copy-cat 📋🐱

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Windows-Supported-green.svg)](https://www.microsoft.com/windows/)
[![License](https://img.shields.io/badge/License-定制协议-orange.svg)](LICENSE.txt)

一个智能的USB文件监控和备份程序，像猫一样悄无声息地守护您的数据安全。

## ✨ 特性亮点

### 🎯 核心功能
- **自动监控**：实时检测U盘插入，无需人工干预
- **智能筛选**：根据关键词自动备份指定类型的文件
- **后台运行**：无窗口、静默运行，不打扰用户工作
- **开机自启**：系统启动时自动运行，持续保护
- **详细日志**：完整的操作记录，便于审计和排查

### 🔒 安全特性
- **零权限要求**：无需管理员权限，所有操作在用户权限内完成
- **路径安全**：防止路径遍历攻击，确保系统安全
- **文件验证**：检查文件类型和大小，避免危险文件
- **隐私保护**：所有数据保存在本地，不上传任何信息

### 🛡️ 兼容性
- ✅ 兼容火绒、360等主流安全软件
- ✅ Windows 7/8/10/11 全平台支持
- ✅ 无需安装Python环境（提供打包版本）

## 📁 项目结构

```
copy-cat/
├── main_hidden.py          # 后台主程序（无窗口）
├── config_gui.py           # 图形配置界面
├── service_manager.py      # 服务管理器
├── build_copy_cat.py       # 一键打包脚本
├── build.bat              # 快速打包批处理
├── config.py              # 配置处理模块
├── logger.py              # 日志系统模块
├── file_handler.py        # 文件处理模块
├── monitor.py             # USB监控模块
├── config.ini             # 配置文件
├── copy-cat.ico           # 程序图标（自定义）
├── requirements.txt       # Python依赖包
└── README.md             # 本文档
```

## 🚀 快速开始

### 方法一：直接运行Python版本

1. **安装依赖**
```bash
pip install psutil pywin32
```

2. **启动程序**
```bash
python main_hidden.py
```

3. **安装为开机启动**
```bash
python main_hidden.py install
```

### 方法二：使用打包的EXE版本

1. **下载最新发布版本**
   - `copy-cat.exe` - 后台主程序
   - `copy-cat_GUI.exe` - 配置界面
   - `copy-cat_Manager.exe` - 服务管理器

2. **运行主程序**
   - 双击 `copy-cat.exe`（后台无窗口运行）
   - 或使用命令行：`copy-cat.exe install`（安装为开机启动）

3. **使用配置界面**
   - 双击 `copy-cat_GUI.exe` 打开图形配置界面

## ⚙️ 配置说明

### 配置文件 (config.ini)
程序首次运行会自动创建配置文件：

```ini
[Settings]
# 要备份的文件类型（扩展名），用逗号分隔
keywords = .doc,.docx,.pdf,.txt,.xlsx,.xls,.pptx,.ppt,.jpg,.png

# 备份目标文件夹
target_folder = C:\copy-cat_backup

# 检查间隔（秒）
check_interval = 5

# 是否记录所有U盘插入事件
log_all_usb = true

[Logging]
# 日志文件路径
log_file = copy-cat.log

# 日志级别：DEBUG, INFO, WARNING, ERROR
log_level = INFO

# 最大日志文件大小（MB）
max_log_size = 10

[Security]
# 最大文件大小限制（MB）
max_file_size = 100

# 排除的驱动器（不监控的盘符）
exclude_drives = C
```

### 通过GUI配置
运行 `copy-cat_GUI.exe` 可以：
- 直观地修改所有配置项
- 选择备份目标文件夹
- 测试配置是否生效
- 立即启动监控程序

## 📊 日志系统

程序生成多层次的日志文件，便于监控和排查：

### 主要日志文件
1. **copy-cat.log** - 主程序运行日志
2. **copy_cat_service.log** - 后台服务日志
3. **copy_cat_status.log** - 程序状态日志
4. **service_error.log** - 错误日志
5. **usb_history.txt** - U盘插入历史记录

### 日志内容示例
```
2024-12-14 10:30:25 - INFO - USB插入 - 驱动器: E: - 名称: 我的U盘
2024-12-14 10:30:28 - INFO - 文件复制成功: 工作报告.docx -> C:\copy-cat_backup\2024-12-14\我的U盘\工作报告.docx
2024-12-14 10:30:30 - INFO - 从 E: 复制了 3 个文件
```

## 🛠️ 高级使用

### 命令行参数
```bash
# 后台主程序
copy-cat.exe              # 启动监控
copy-cat.exe install      # 安装为开机启动
copy-cat.exe uninstall    # 移除开机启动
copy-cat.exe help         # 显示帮助信息

# 服务管理器
copy-cat_Manager.exe      # 显示管理菜单
copy-cat_Manager.exe start     # 启动服务
copy-cat_Manager.exe stop      # 停止服务
copy-cat_Manager.exe status    # 查看状态
```

### 服务管理
使用 `copy-cat_Manager.exe` 可以：
- ✅ 启动/停止后台服务
- ✅ 安装/卸载开机启动
- ✅ 查看运行状态
- ✅ 查看日志文件
- ✅ 管理程序配置

### 备份文件结构
```
C:\copy-cat_backup\
├── 2024-12-14\           # 按日期分类
│   ├── 我的U盘\         # 按U盘名称分类
│   │   ├── 文档\        # 保持原始目录结构
│   │   │   └── 报告.docx
│   │   └── 图片.jpg
│   └── USB_D_20241214\
└── usb_history.txt      # U盘使用记录
```

## 🔧 自定义打包

### 准备自定义图标
1. 将您的图标文件命名为 `copy-cat.ico`
2. 放在项目根目录下
3. 支持的图标文件名：`copy-cat.ico`、`icon.ico`、`custom.ico`

### 打包为EXE
```bash
# 安装打包依赖
pip install pyinstaller psutil pywin32 Pillow

# 运行打包脚本
python build_copy_cat.py
```

### 打包选项
- 选项3：使用自定义图标打包
- 选项8：一键构建所有EXE文件
- 选项9：创建安装程序（需要Inno Setup）

## 📋 使用场景

### 🏢 办公环境
- 自动备份U盘中的重要文档
- 防止文件意外丢失
- 审计文件传输记录

### 🎓 教育机构
- 收集学生作业文件
- 备份教学资料
- 管理多媒体文件

### 💼 个人使用
- 自动整理U盘照片
- 备份重要文档
- 监控文件传输

## ⚠️ 注意事项

### 法律合规
1. **合法使用**：仅用于您拥有权限的文件备份
2. **隐私尊重**：不得用于监控他人隐私数据
3. **遵守法规**：遵守当地数据保护法律法规

### 技术限制
1. **文件大小**：默认最大100MB，可在配置中调整
2. **文件类型**：默认备份常见办公文档和图片
3. **驱动器排除**：默认排除系统盘C:

### 兼容性问题
如果安全软件报警，请：
1. 将程序添加到信任列表
2. 参考 `火绒安全兼容说明.txt`
3. 检查日志文件了解详细情况

## 🔍 故障排查

### 常见问题

**Q: 程序运行但没有反应？**
A: 程序在后台运行，请查看日志文件了解状态。

**Q: 如何停止程序？**
A: 使用任务管理器结束 `copy-cat.exe` 进程，或运行 `copy-cat_Manager.exe stop`。

**Q: 备份的文件在哪里？**
A: 默认在 `C:\copy-cat_backup`，可在配置中修改。

**Q: 如何查看运行日志？**
A: 使用服务管理器查看，或直接打开日志文件。

### 诊断步骤
1. 检查 `service_error.log` 是否有错误信息
2. 查看 `copy_cat_status.log` 了解程序状态
3. 确认配置文件 `config.ini` 是否正确
4. 检查是否有足够的磁盘空间

## 🤝 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. **Fork 本仓库**
2. **创建功能分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **开启 Pull Request**

### 开发环境设置
```bash
# 克隆仓库
git clone https://github.com/yourusername/copy-cat.git
cd copy-cat

# 安装开发依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/
```

## 📄 许可证

本项目采用定制许可证，详见 [LICENSE.txt](LICENSE.txt)。

### 使用条款
1. 本程序仅供合法的USB文件备份目的使用
2. 禁止用于非法监控或侵犯他人隐私
3. 使用者需遵守当地法律法规
4. 程序作者不承担任何滥用责任

## 📞 支持与联系

### 获取帮助
- 📖 查看本文档和配置说明
- 📁 检查日志文件了解详细情况
- 🐛 提交Issue报告问题

### 反馈渠道
- GitHub Issues: [问题反馈](https://github.com/neweryuop-SD/copy-cat/issues)
- 电子邮件: neweryuop2@qq.com

## 📈 版本历史

### v2.0 (当前版本)
- ✅ 重命名为 copy-cat
- ✅ 支持自定义图标
- ✅ 增强安全特性
- ✅ 改进后台运行稳定性
- ✅ 添加服务管理器

### v1.0 (初始版本)
- ✅ 基础USB监控功能
- ✅ 文件自动备份
- ✅ 开机自启动
- ✅ 日志记录系统

---

**注意**：本程序是开源工具，作者不对滥用行为负责。请确保在合法合规的前提下使用，尊重他人隐私和版权。

---
<div align="center">
<sub>Built with ❤️ by copy-cat development team</sub><br>
<sub>© 2024 copy-cat project. All rights reserved.</sub>
</div>