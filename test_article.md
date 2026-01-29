# 使用 Claude Code Skills 发布微信公众号文章

这是一篇测试文章，用于演示如何使用 **mp-weixin-skills** 工具将 Markdown 文档发布到微信公众号草稿箱。

## 什么是 mp-weixin-skills？

**mp-weixin-skills** 是一个强大的微信公众号文章发布工具，它是为 Claude Code 设计的 Skill，可以帮助你：

- 📝 将 Markdown 文档转换为微信公众号格式
- 🎨 自动生成符合微信规格的封面图片
- 📤 自动上传素材到微信素材库
- 🚀 一键推送到草稿箱

## 核心功能

### 1. 文档解析

支持从 Markdown 文档中提取：
- 标题（自动识别第一个一级标题）
- 正文内容
- 图片引用
- 代码块

### 2. 样式转换

将 Markdown 转换为符合微信公众号要求的 HTML：
- 内联 CSS 样式
- 响应式布局
- 代码高亮
- 引用块美化

### 3. 封面生成

支持三种封面生成方式：
- **本地模板**: 使用预设模板生成（始终可用）
- **AI 生成**: 使用 DALL-E 等AI服务
- **图库搜索**: 从 Unsplash/Pexels 搜索高质量图片

### 4. API 集成

直接对接微信公众号 API：
- 自动获取 access_token
- 上传封面图片到素材库
- 创建草稿到草稿箱
- 支持更新已有草稿

## 使用方法

### 基本用法

```bash
mp-weixin publish article.md
```

### 手动模式

```bash
mp-weixin publish article.md --no-api
```

### 更新草稿

```bash
mp-weixin update <media_id>
```

## 技术架构

工具采用模块化设计，包含以下核心模块：

| 模块 | 功能 |
|------|------|
| 文档解析器 | 解析 MD/Word/PDF 文档 |
| 内容转换器 | 转换为微信公众号 HTML |
| 封面生成器 | 生成封面图片 |
| API 客户端 | 对接微信公众号 API |

## 代码示例

```python
# 示例：发布文章
from src.cli import main

main(['publish', 'my-article.md'])
```

## 总结

**mp-weixin-skills** 让内容发布变得简单高效！

- ✅ 省时：一键发布，无需手动操作
- ✅ 便捷：自动化处理封面和素材
- ✅ 稳定：完善的错误处理和日志

---

*本文由 mp-weixin-skills 自动生成并发布*
