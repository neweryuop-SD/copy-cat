# copy-cat 图标设置说明

## 如何设置自定义图标

### 方法1：直接放置图标文件
将您的图标文件（必须是 `.ico` 格式）放在项目根目录，命名为以下任意一个名称：

1. `copy-cat.ico` (推荐)
2. `icon.ico`
3. `custom.ico`

### 方法2：转换其他格式为ICO
如果您有PNG、JPG等格式的图片，可以使用以下工具转换为ICO：

#### 在线转换工具：
1. [ConvertICO](https://convertico.com/)
2. [ICO Convert](https://icoconvert.com/)

#### 使用Python转换（需要Pillow）：
```python
from PIL import Image

# 打开图片文件
img = Image.open('your_image.png')

# 保存为ICO
img.save('copy-cat.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])