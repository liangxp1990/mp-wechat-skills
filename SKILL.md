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
