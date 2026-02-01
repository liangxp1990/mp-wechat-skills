# 图片素材上传参考

## 上传图片到微信素材库

当文章中包含图片时，需要先将图片上传到微信公众号素材库，然后在 HTML 中引用素材的 media_id。

## 批量上传图片命令

### 上传单张图片

```bash
# 上传为图片
python3 scripts/cli.py upload-image cover.jpg

# 上传为缩略图
python3 scripts/cli.py upload-image cover.jpg --type thumb
```

### 批量上传

```bash
# 上传 images 文件夹中的所有 JPG 图片
python3 scripts/cli.py upload-images ./images

# 上传所有 PNG 图片
python3 scripts/cli.py upload-images ./photos --pattern "*.png"

# 上传为缩略图
python3 scripts/cli.py upload-images ./covers --type thumb
```

## 图片格式规范

### 格式和大小限制

| 类型 | 支持格式 | 大小限制 | 用途 |
|------|----------|----------|------|
| thumb | JPG, PNG | ≤ 2MB | 封面缩略图 |
| image | JPG, PNG | ≤ 5MB | 正文图片 |

### 推荐尺寸

| 类型 | 推荐尺寸 | 比例 |
|------|----------|------|
| 封面图 | 1080×460 或 1080×607 | 2.35:1 或 16:9 |
| 正文图 | 宽度 ≤ 900px | 自适应高度 |
| 长图 | 宽度 1080px | 高度不限 |
| 方图 | 1080×1080 | 1:1 |

## AI 处理图片上传流程

当 Claude Code 识别到文章包含本地图片引用时：

1. **扫描图片引用** - 从 HTML/Markdown 中提取图片路径
2. **批量上传** - 调用 `upload-images` 命令上传所有图片
3. **替换链接** - 将本地路径替换为微信素材库的 URL
4. **验证完整性** - 确保所有图片都成功上传

**示例提示词：**
```
请将文章中引用的所有本地图片上传到微信公众号素材库，
并更新 HTML 中的图片链接为微信 CDN 地址。
```

## 图片优化建议

### 上传前处理

**压缩工具：**
- TinyPNG (https://tinypng.com) - 在线压缩
- ImageOptim (Mac) - 本地工具
- Squoosh (Google) - 开源工具

**压缩目标：**
- 单张图片 ≤ 500KB（提升加载速度）
- 保持视觉质量
- 统一图片宽度（建议 900px）

**格式选择：**
- 照片：JPEG (质量 80-85%)
- 图标/图形：PNG (无损)
- 动图：GIF (简短动画)

### 移动端优化

1. **单张图片 ≤ 500KB** - 提升加载速度
2. **避免超大尺寸** - 不超过 2000px
3. **使用渐进式 JPEG** - 逐步加载体验
4. **考虑懒加载** - 微信自动处理

### 水印处理

**是否添加水印：**
- 原创内容：建议添加
- 转载内容：遵守原作者要求
- 商业图片：按授权要求

**水印位置：**
- 右下角（不影响阅读）
- 半透明（不遮挡内容）
- 小巧精致（不过于显眼）

## 图片资源管理

### 文件夹结构建议

```
project/
├── images/
│   ├── covers/        # 封面图
│   ├── content/       # 正文配图
│   ├── icons/         # 图标素材
│   └── screenshots/   # 截图
└── articles/
    └── article-images/  # 文章专属图片
```

### 命名规范

**推荐格式：**
- 日期+描述：`2024-01-15-python-tutorial.jpg`
- 文章名+序号：`article-name-01.jpg`
- 描述性名称：`wechat-api-flowchart.png`

**避免：**
- 中文文件名（可能兼容性问题）
- 特殊字符
- 过长的文件名

## 批量处理脚本

### 使用 Python 批量压缩

```python
from PIL import Image
import os

def compress_images(input_dir, output_dir, quality=85, max_width=900):
    """批量压缩图片"""
    for filename in os.listdir(input_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            img = Image.open(os.path.join(input_dir, filename))

            # 调整宽度
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height))

            # 保存压缩后的图片
            img.save(
                os.path.join(output_dir, filename),
                quality=quality,
                optimize=True
            )
```

## 常见问题

### Q1: 上传失败怎么办？

**可能原因：**
1. 图片尺寸不符合要求
2. 文件过大
3. 网络问题
4. API 配额限制

**解决方法：**
1. 检查并调整图片尺寸
2. 压缩图片大小
3. 检查网络连接
4. 稍后重试

### Q2: 图片显示模糊？

**可能原因：**
1. 原图分辨率低
2. 过度压缩
3. 尺寸不匹配

**解决方法：**
1. 使用高分辨率原图（≥1080px）
2. 控制压缩质量（≥80%）
3. 按推荐尺寸准备图片

### Q3: 如何批量替换图片？

**方法：**
1. 上传新图片到素材库
2. 获取新的 media_id
3. 更新文章 HTML 中的图片引用
4. 更新草稿

## 图片 CDN 说明

微信会自动将上传的图片分发到 CDN：

**特点：**
- 全球加速
- 自动适配
- 智能压缩
- 缓存优化

**URL 格式：**
```
https://mmbiz.qpic.cn/mmbiz_jpg/xxx/0?wx_fmt=jpeg
```

**注意事项：**
- CDN URL 是永久有效的
- 不要修改原始 URL
- 删除素材后 URL 会失效
