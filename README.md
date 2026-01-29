# 微信公众号文章发布工具

一个强大的微信公众号文章发布工具，将 Markdown、Word 或 PDF 文档转换为符合微信公众号排版要求的 HTML 内容，支持自动生成封面、上传素材到微信素材库，并推送到草稿箱。

## 功能特点

- **多格式支持**: 支持 Markdown (.md)、Word (.docx)、PDF (.pdf) 格式
- **智能封面生成**: 支持 AI 生成、图库搜索、本地模板三种方式
- **自动素材上传**: 自动将图片上传到微信公众号素材库
- **样式模板系统**: 提供多种预设样式模板，支持自定义主题色
- **API 和手动模式**: 支持自动 API 发布和手动复制两种模式
- **草稿管理**: 支持创建新草稿和更新已有草稿
- **详细日志**: 清晰的日志输出，便于调试和排查问题

## 使用方法

### 基本使用

```bash
# 发布文章到微信公众号草稿箱
mp-weixin publish article.md

# 指定封面生成方式
mp-weixin publish article.md --cover-type ai

# 使用指定样式模板
mp-weixin publish article.md --template modern

# 仅转换格式（不上传）
mp-weixin publish article.md --no-api
```

### 更新已有草稿

```bash
# 更新已发布的草稿
mp-weixin update <media_id>

# 更新并重新生成封面
mp-weixin update <media_id> --regenerate-cover
```

### 环境配置

创建 `.env` 文件配置微信公众号 API：

```bash
# 微信公众号配置（必需）
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret

# 封面生成配置（可选）
COVER_GENERATOR=auto
OPENAI_API_KEY=your_openai_key
UNSPLASH_API_KEY=your_unsplash_key

# 输出配置
OUTPUT_DIR=./output
TEMPLATE_NAME=default
THEME_COLOR=#07c160

# 日志配置
LOG_LEVEL=INFO
```

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                     CLI 入口                             │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ 文档解析器   │  │ 内容转换器    │  │  封面生成器    │  │
│  │ MD/PDF/DOC  │→ │ HTML+CSS     │→ │ AI/搜索/模板   │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
│         ↓                  ↓                ↓           │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ 图片处理器   │  │ 样式应用器    │  │  素材上传器    │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
│                                            ↓             │
│                                  ┌─────────────────┐    │
│                                  │ 微信公众号API    │    │
│                                  │ - 上传素材       │    │
│                                  │ - 创建/更新草稿  │    │
│                                  └─────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 技术栈

- **Python 3.10+**
- **文档解析**: markdown-it-py, python-docx, PyMuPDF
- **图片处理**: Pillow
- **HTTP 请求**: requests
- **配置管理**: python-dotenv
- **CLI 框架**: click

## 安装

### 从源码安装

```bash
# 克隆仓库
git clone <repository-url>
cd mp-weixin-skills

# 安装依赖
pip install -e .
```

### 开发环境安装

```bash
# 安装开发依赖
pip install -e ".[dev]"
```

## 开发

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ -v --cov=src
```

### 代码格式化

```bash
# 使用 black 格式化代码
black src/

# 使用 mypy 进行类型检查
mypy src/
```

## 命令参考

### publish - 发布文章

```bash
mp-weixin publish <file> [options]
```

**选项:**
- `--cover-type` - 封面生成方式 (auto|ai|search|template)
- `--template` - 样式模板 (default|modern|classic|tech|minimal)
- `--theme-color` - 主题颜色 (如 #07c160)
- `--api/--no-api` - 是否使用 API
- `--verbose, -v` - 详细输出
- `--env` - 环境文件路径

### update - 更新草稿

```bash
mp-weixin update <media_id> [options]
```

**选项:**
- `--regenerate-cover` - 重新生成封面
- `--source` - 指定新的源文件

### convert - 仅转换

```bash
mp-weixin convert <file> [options]
```

仅转换格式，生成 HTML 和封面，不上传。

## 错误处理

工具提供友好的错误提示和解决方案：

- **配置错误**: 提示缺失的配置项
- **API 错误**: 显示错误码和解决建议
- **文件错误**: 指出具体问题和检查项
- **网络错误**: 提供排查建议

## 样式模板

| 模板 | 风格 | 适用场景 |
|------|------|----------|
| default | 简洁 | 通用内容 |
| modern | 现代 | 卡片风格，视觉层次分明 |
| classic | 经典 | 正式内容，传统媒体风 |
| tech | 技术 | 技术文章，代码友好 |
| minimal | 极简 | 强调内容本身 |

## 项目结构

```
mp-weixin-skills/
├── src/                    # 源代码
│   ├── parsers/           # 文档解析器
│   ├── converters/        # 内容转换器
│   ├── covers/            # 封面生成器
│   ├── wechat/            # 微信公众号 API
│   ├── utils/             # 工具模块
│   ├── config.py          # 配置管理
│   ├── exceptions.py      # 异常定义
│   └── cli.py             # 命令行入口
├── tests/                 # 测试代码
│   ├── test_*.py
│   └── test_integration.py
├── examples/              # 示例文件
├── docs/                  # 文档
├── pyproject.toml         # 项目配置
├── .env.example           # 环境变量示例
└── README.md              # 本文件
```

## 贡献

欢迎贡献代码！请确保：

1. 代码通过所有测试
2. 遵循项目的代码风格
3. 添加必要的测试用例
4. 更新相关文档

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。

---

**注意**: 本工具需要微信公众号 API 权限才能使用自动发布功能。请确保你已获得相应的 API 访问权限。
