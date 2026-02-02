# 封面图生成参考

## 自动封面规格

**标准规格：**
- 尺寸：1080×460 (2.35:1)
- 格式：JPEG
- 质量：95%
- 字体：华文黑体（支持中文）

## 封面生成方式

### 方式 1: 搜索图片二次加工（默认推荐）

**图片来源：**
- Pexels（推荐，免费商用，支持中文搜索）
- Unsplash（免费高质量）
- Pixabay（免费素材）
- 企业自摄图库

**搜索关键词：**

**技术类文章：**
- 「科技背景 抽象」→ 搜索关键词：`artificial intelligence`, `technology`, `coding`
- 「数据可视化」→ 搜索关键词：`data visualization`, `analytics`
- 「代码编辑器」→ 搜索关键词：`code editor`, `programming`
- 「网络连接」→ 搜索关键词：`network`, `connectivity`
- 「云计算」→ 搜索关键词：`cloud computing`

**职场类文章：**
- 「办公场景」→ 搜索关键词：`workspace`, `office`
- 「商务会议」→ 搜索关键词：`business meeting`, `conference`
- 「团队协作」→ 搜索关键词：`teamwork`, `collaboration`
- 「工作空间」→ 搜索关键词：`working space`

**生活类文章：**
- 「自然风景」→ 搜索关键词：`nature`, `landscape`
- 「城市街景」→ 搜索关键词：`city`, `urban`
- 「温馨家居」→ 搜索关键词：`home interior`, `cozy`
- 「美食摄影」→ 搜索关键词：`food`, `cooking`
- 「旅行风光」→ 搜索关键词：`travel`, `adventure`

**AI 操作步骤（使用浏览器自动化）：**

当 AI 需要生成封面时，请按照以下步骤操作：

1. **分析文章主题**，提取关键词
   - 识别文章属于技术/职场/生活哪一类
   - 选择对应的英文搜索关键词

2. **使用浏览器 MCP 搜索图片**

   使用任何可用的浏览器 MCP（如 Chrome DevTools MCP、dev-browser、agent-browser）执行以下操作：

   **导航到 Pexels 搜索页面：**
   ```python
   # 使用浏览器 MCP 的导航功能
   navigate_page("https://www.pexels.com/zh-cn/search/[关键词]/")
   ```

3. **提取图片链接**

   使用浏览器 MCP 的脚本执行功能提取页面中的图片 URL：

   ```python
   # 使用浏览器 MCP 的脚本执行功能
   results = evaluate_script("""
       () => {
           const imgs = document.querySelectorAll('img');
           const imageUrls = [];
           imgs.forEach(img => {
               const src = img.src || img.getAttribute('data-src');
               if (src && src.includes('pexels')) {
                   imageUrls.push(src);
               }
           });
           return imageUrls;
       }
   """)
   # 选择第一张图片
   image_url = results[0]
   ```

4. **下载图片到本地**
   ```python
   import requests
   from pathlib import Path
   from datetime import datetime

   # 下载图片
   temp_dir = Path("temp")
   temp_file = temp_dir / f"cover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

   response = requests.get(image_url, timeout=30)
   response.raise_for_status()

   with open(temp_file, 'wb') as f:
       f.write(response.content)
   ```

5. **使用 PIL 进行二次加工**
   ```python
   from PIL import Image, ImageDraw, ImageFont

   # 打开并调整尺寸
   img = Image.open(temp_file)
   img = img.resize((1080, 460), Image.Resampling.LANCZOS)

   # 添加渐变遮罩（底部深色）
   overlay = Image.new('RGBA', (1080, 460), (0, 0, 0, 0))
   for y in range(460 - 150, 460):
       alpha = int((y - (460 - 150)) / 150 * 180)
       for x in range(1080):
           overlay.putpixel((x, y), (0, 0, 0, alpha))

   img = Image.alpha_composite(img.convert('RGBA'), overlay)

   # 添加标题文字
   draw = ImageDraw.Draw(img)
   title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 56)

   # 截断过长标题（18字符）
   if len(title) > 18:
       title = title[:18] + "..."

   text_y = 460 - 120

   # 文字阴影
   for offset in range(2, 0, -1):
       draw.text((540 + offset, text_y + offset), title,
                font=title_font, fill=(0, 0, 0, 100), anchor="mm")

   # 白色文字
   draw.text((540, text_y), title,
            font=title_font, fill=(255, 255, 255, 255), anchor="mm")

   # 保存
   img = img.convert('RGB')
   img.save(temp_file, 'JPEG', quality=95)
   ```

**优点：**
- 图片质量高
- 风格多样
- 成本低
- 无需 API key
- 适合大多数场景

**适用场景：**
- 默认方式，适用于所有文章

### 方式 2: AI 生成封面（重要文章）

**工具选择：**
- **Claude AI** - 文字描述生成
- **Midjourney** - 艺术风格
- **DALL·E 3** - 精确控制
- **Stable Diffusion** - 开源方案

**提示词模板：**
```
Create a cover image for an article about "[文章主题]".
Style: [风格描述]
Colors: [配色方案]
Elements: [包含元素]
Mood: [氛围]
```

**示例提示词：**
```
Create a modern, professional cover image for an article about Python programming.
Style: Clean, tech-forward with subtle code elements in background
Colors: Blue and yellow accent on dark background
Elements: Abstract code snippets, Python logo silhouette
Mood: Professional, educational, inspiring
Composition: Leave right side empty for title overlay
```

**优点：**
- 原创设计
- 高度定制
- 视觉冲击力强

**适用场景：**
- 重要文章
- 系列专栏
- 品牌建设

### 方式 3: 模板生成（备选）

**特点：**
- 自动使用文章标题生成
- 渐变背景（基于主题色）
- 右侧装饰条、左上角几何图形
- 底部装饰线和圆点、文字阴影效果

**优点：**
- 快速自动生成
- 风格统一
- 无需额外资源

**适用场景：**
- 网络不可用时
- 作为搜索方式的回退方案

## 封面设计原则

### 视觉层次

1. **主标题** - 最醒目，位置居中或偏左
2. **装饰元素** - 辅助，不抢眼
3. **背景** - 烘托氛围，不干扰文字

### 颜色搭配

**单色系：**
- 主色 + 深浅变化
- 统一和谐

**对比色：**
- 主题色 + 补色点缀
- 醒目突出

**渐变色：**
- 同色渐变
- 增加层次感

### 文字处理

**字体选择：**
- 中文：华文黑体、思源黑体
- 英文：Roboto、Open Sans、Montserrat

**大小建议：**
- 主标题：48-64px
- 副标题：24-32px
- 装饰文字：16-20px

**可读性：**
- 确保对比度足够
- 添加文字阴影
- 避免复杂背景

### 构图技巧

**三分法：**
- 主体放在交叉点
- 视觉更平衡

**留白：**
- 不要填满所有空间
- 给文字留出位置

**引导线：**
- 用元素引导视线
- 指向标题或重点

## 封面优化建议

✅ **要做：**
1. 使用高质量图片作为底图（分辨率≥1080px）
2. 选择与文章主题相关的视觉元素
3. 确保标题文字清晰可读
4. 保持品牌色的一致性
5. 测试在不同设备上的显示效果

⚠️ **避免：**
1. 使用版权不明的图片
2. 过于复杂的背景影响文字识别
3. 颜色过于花哨
4. 文字过小或过多
5. 与品牌风格不符

## 封面测试清单

发布前检查：
- [ ] 尺寸是否符合 1080×460
- [ ] 标题文字是否清晰可读
- [ ] 颜色对比度是否足够
- [ ] 与文章主题是否相关
- [ ] 品牌色是否一致
- [ ] 在手机上预览效果
- [ ] 文件大小是否合理（<500KB）
- [ ] 版权是否合规

## 批量封面生成

对于系列文章，可以创建模板：

**模板元素：**
- 固定布局结构
- 统一的装饰元素
- 品牌色系
- 字体样式

**可变元素：**
- 文章标题
- 主题图片
- 配色微调

**工作流程：**
1. 创建基础模板
2. 批量替换标题
3. 调整主题图片
4. 导出系列封面
