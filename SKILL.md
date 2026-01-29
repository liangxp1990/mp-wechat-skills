---
name: mp-weixin-skills
description: 使用此 skill 将 Markdown 文档转换为微信公众号格式并发布到草稿箱
---

# 微信公众号文章发布工具

## Overview

将 Markdown 文档转换为符合微信公众号排版的 HTML 内容，自动生成封面、上传素材到微信素材库，并推送到草稿箱。

**Core principle:** 自动化处理内容发布流程，从文档转换到 API 上传一键完成。

## When to Use

- 需要定期发布文章到微信公众号
- 有大量 Markdown 文档需要转换为微信格式
- 希望自动化封面生成和素材上传流程

**使用前准备:**
1. 配置微信公众号 API 凭证（AppID 和 AppSecret）
2. 配置服务器 IP 白名单
3. 确保有稳定的网络连接

## 最佳实践

### 标题规范

**标题长度:**
- 建议：10-20 个字符
- 上限：会自动截断为 18 个字符

**标题格式:**
```markdown
# 主标题（使用一级标题）
## 章节标题（使用二级标题）
```

**一级标题样式（自动应用）:**
- ✅ 主题色渐变背景（从主题色到淡化色）
- ✅ 白色文字，增强对比度
- ✅ 圆角边框（8px）
- ✅ 阴影效果（文字和卡片阴影）
- ✅ 内边距（20px 上下，24px 左右）

**二级标题样式（自动应用）:**
- ✅ 左侧主题色装饰条（4px）
- ✅ 12px 左内边距

**标题建议:**
- ✅ 使用吸引人的标题，如 "3 个技巧让你..."
- ✅ 加入数字增加吸引力
- ✅ 突出核心价值点
- ❌ 避免过于抽象的标题

**标题效果示例:**
```
┌─────────────────────────────────────┐
│  标题文字（渐变背景，白色文字）       │
└─────────────────────────────────────┘

章节标题
│ 左侧装饰条 标题文字
```

### 排版优化

**段落间距:**
- 每段之间空一行
- 避免大段文字堆砌

**标题层级:**
```markdown
# 一级标题（文章标题）
## 二级标题（章节）
### 三级标题（小节）
```

**列表使用:**
- 无序列表：使用 `-` 或 `*`
- 有序列表：使用 `1.` `2.` `3.`

**代码块:**
````markdown
```python
代码内容
```
````

**引用块:**
```markdown
> 这是引用内容
```

**表格:**
```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 内容 | 内容 | 内容 |
```

### 封面图生成

**自动封面规格:**
- 尺寸: 1080×460 (2.35:1)
- 格式: JPEG
- 质量: 95%
- 字体: 华文黑体（支持中文）

**封面设计元素:**
- 渐变背景（基于主题色）
- 右侧装饰条
- 左上角几何图形
- 底部装饰线和圆点
- 文字阴影效果

**自定义主题色:**
```bash
mp-weixin publish article.md --theme-color "#ff6b6b"
```

**推荐主题色:**
| 色值 | 适用场景 |
|------|----------|
| `#07c160` | 科技、效率 |
| `#ff6b6b` | 生活、情感 |
| `#4a90e2` | 商业、职场 |
| `#f5a623` | 教育、培训 |
| `#9013fe` | 创意、设计 |

### 内容优化

**文章结构:**
```
标题
├── 引言（1-2 段）
├── 主体（3-5 个章节）
│   ├── 小标题
│   ├── 内容
│   └── 示例/配图
├── 总结（1 段）
└── 行动号召（可选）
```

**写作建议:**
1. **开篇吸引**: 前 3 秒决定读者是否继续阅读
2. **结构清晰**: 使用小标题分隔内容
3. **段落简短**: 每段 3-5 句话为宜
4. **多用列表**: 提高可读性
5. **加入配图**: 每 300-500 字配一张图

**代码示例:**
```markdown
## 标题

引言内容...

### 核心概念

- 要点一
- 要点二
- 要点三

### 代码示例

```python
def example():
    return "Hello"
```

## Command Reference

### publish - 发布文章

```bash
mp-weixin publish <file> [options]
```

**选项:**
- `--template` - 样式模板 (default/modern/classic/tech/minimal)
- `--theme-color` - 主题颜色 (如 #07c160)
- `--no-api` - 不使用 API，仅生成 HTML 文件
- `--verbose, -v` - 详细输出

**示例:**
```bash
mp-weixin publish article.md
mp-weixin publish article.md --template modern
mp-weixin publish article.md --theme-color "#ff6b6b"
mp-weixin publish article.md --no-api
```

### update - 更新草稿

```bash
mp-weixin update <media_id> [options]
```

**选项:**
- `--source` - 指定新的源文件
- `--regenerate-cover` - 重新生成封面

**示例:**
```bash
mp-weixin update <media_id>
mp-weixin update <media_id> --regenerate-cover
mp-weixin update <media_id> --source new-article.md
```

### version - 显示版本

```bash
mp-weixin version
```

## Configuration

### 环境变量 (.env)

```bash
# 微信公众号配置（必需）
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret

# 输出配置
OUTPUT_DIR=./output
TEMPLATE_NAME=default
THEME_COLOR=#07c160

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=mp_weixin.log
```

### IP 白名单配置

1. 登录微信公众平台
2. 进入「开发 → 基本配置」
3. 找到「IP 白名单」
4. 添加服务器公网 IP
5. 等待 5-15 分钟生效

## Error Handling

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 40001 | AppSecret 错误 | 检查 AppSecret 是否正确 |
| 40164 | IP 不在白名单 | 配置 IP 白名单，等待生效 |
| 45009 | 接口调用超过限制 | 等待限制重置 |
