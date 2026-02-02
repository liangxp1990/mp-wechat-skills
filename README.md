# 微信公众号文章管理 Skill 市场

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![plugins](https://img.shields.io/badge/plugins-1-green.svg)](https://github.com/liangxp/mp-wechat-skills)

## 概述

这是一个专门用于管理微信公众号文章发布的 Claude Code Skill 市场。当您需要将文章发布到微信公众号时，此 Skill 会：

1. **首先要求 AI 将文章转换为微信公众号格式的 HTML**
2. **然后使用 Python 脚本上传素材和创建草稿**

## 核心原则

- **AI 负责**：文档转换（Markdown/Word/PDF → 微信公众号 HTML）
- **Skill 负责**：微信 API 操作（上传素材、草稿管理）

## 安装

### 前置要求

| 要求 | 检查 | 安装 |
|------|------|------|
| Claude Code CLI | `claude --version` | [入门指南](https://claude.ai/code) |

### 快速安装

在终端（非 Claude Code 内部）运行：

```bash
# 1. 添加技能市场
claude plugin marketplace add liangxp1990/mp-wechat-skills

# 2. 安装技能
claude plugin install mp-weixin-skills@mp-weixin-skills
```

### 验证安装

```bash
# 检查市场是否已注册
claude plugin marketplace list

# 检查插件是否已安装
claude plugin list
```

## 使用

### 配置微信公众号 API 凭证

创建 `.env` 文件：

```bash
# 微信公众号配置（必需）
WECHAT_APP_ID=your_app_id_here
WECHAT_APP_SECRET=your_app_secret_here

# 输出配置（可选）
OUTPUT_DIR=./output
TEMP_DIR=./temp

# 样式配置（可选）
TEMPLATE_NAME=default
THEME_COLOR=#07c160
```

### 基本使用场景

**场景 1: 发布新文章到草稿箱**

```
请使用 mp-weixin-skills 将 article.md 发布到微信公众号草稿箱
```

**场景 2: 更新已有草稿**

```
请使用 mp-weixin-skills 更新草稿 media_id_xxx 的内容为 article.md
```

**场景 3: 上传图片素材**

```
请使用 mp-weixin-skills 上传 image.png 到微信素材库
```

## 目录结构

```
mp-wechat-skills/
├── .claude-plugin/
│   ├── plugin.json          # 市场元数据
│   └── marketplace.json     # 插件注册表
├── plugins/
│   └── mp-weixin-skills/    # 技能目录
│       ├── plugin.json      # 技能元数据
│       ├── SKILL.md         # 技能定义
│       ├── scripts/         # Python 脚本
│       ├── references/      # 支持文档
│       └── examples/        # 示例文章
└── README.md
```

## 更新市场

当有新版本发布时：

```bash
# 更新市场仓库
cd ~/.claude/plugins/marketplaces/mp-wechat-skills
git pull

# 重新安装更新的技能
claude plugin install mp-weixin-skills@mp-weixin-skills
```

## 故障排除

### "Source path does not exist" 错误

**原因**：市场仓库不同步或有旧数据。

**修复**：
```bash
cd ~/.claude/plugins/marketplaces/mp-wechat-skills
git pull
claude plugin install mp-weixin-skills@mp-weixin-skills
```

### 技能未显示

**原因**：插件已安装但命令未被发现。

**修复**：
1. 验证插件是否安装：
   ```bash
   cat ~/.claude/plugins/installed_plugins.json | grep "mp-weixin-skills"
   ```
2. 重启 Claude Code
3. 清除缓存并重新安装：
   ```bash
   rm -rf ~/.claude/plugins/cache/mp-weixin-skills
   claude plugin install mp-weixin-skills@mp-weixin-skills
   ```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 作者

liangxp - [GitHub](https://github.com/liangxp)

## 相关资源

- [Claude Code 官方文档](https://claude.ai/code)
- [微信公众号开发文档](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html)
- [cc-skills 市场参考](https://github.com/terrylica/cc-skills)
