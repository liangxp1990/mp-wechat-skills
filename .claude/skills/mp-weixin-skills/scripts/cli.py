"""命令行接口"""

import sys
import logging
from pathlib import Path
import click

from config import AppConfig
from utils.logger import setup_logging
from parsers import ParserFactory
from converters import WechatHTMLBuilder
from covers.template_maker import TemplateCoverGenerator
from wechat import WechatApiClient, WechatConfig
from exceptions import MpWeixinError

logger = logging.getLogger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="详细输出")
@click.option("--env", default=".env", help="环境文件路径（相对于 project-path 或绝对路径）")
@click.option("--project-path", help="项目根目录路径（用于解析相对路径）")
@click.pass_context
def main(ctx: click.Context, verbose: bool, env: str, project_path: str):
    """微信公众号文章发布工具

    一个强大的工具，将 Markdown 文档转换为符合微信公众号排版要求的格式。
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["project_path"] = project_path

    # 解析 env 文件路径
    env_path = Path(env)
    if not env_path.is_absolute() and project_path:
        # 如果 env 是相对路径且有 project_path，则拼接
        env_path = Path(project_path) / env
    ctx.obj["env"] = str(env_path)


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--template", default="default", help="样式模板名称")
@click.option("--cover-type", default="template", help="封面生成方式 (template)")
@click.pass_context
def publish(ctx: click.Context, file: str, template: str, cover_type: str):
    """发布文章到微信公众号

    将 Markdown 文件转换为微信公众号格式，并自动上传到草稿箱。

    示例:

        mp-weixin publish article.md                    # 使用 API 上传到草稿箱

        mp-weixin publish article.md --template fancy  # 使用指定模板
    """
    try:
        # 加载配置
        config = AppConfig.from_env(ctx.obj["env"])
        log_level = "DEBUG" if ctx.obj["verbose"] else config.log_level
        setup_logging(log_level, config.log_file)

        logger.info("[CLI] 微信公众号文章发布工具启动")

        # 检查微信 API 配置
        if not config.has_wechat_api():
            click.echo("❌ 未配置微信公众号 API 凭证")
            click.echo("\n请在项目根目录的 .env 文件中添加以下配置：")
            click.echo("\n  WECHAT_APP_ID=your_app_id")
            click.echo("  WECHAT_APP_SECRET=your_app_secret")
            click.echo("\n获取方式：")
            click.echo("  1. 登录微信公众平台 https://mp.weixin.qq.com")
            click.echo("  2. 进入「开发 → 基本配置」")
            click.echo("  3. 查看「开发者ID (AppID)」和「开发者密码 (AppSecret)」")
            click.echo("\n配置完成后，请重新运行命令。")
            sys.exit(1)

        # 解析文档
        file_path = Path(file)
        parser = ParserFactory.get_parser(file_path)
        parsed = parser.parse(file_path)

        logger.info(f"[CLI] 文章标题: {parsed.title}")

        # 转换内容
        builder = WechatHTMLBuilder(template)
        html_content = builder.build(parsed)

        # 生成封面
        cover_gen = TemplateCoverGenerator(config.theme_color)
        cover_result = cover_gen.generate(parsed.title, "")

        # API 模式
        logger.info("[CLI] 运行在 API 模式")

        api_config = WechatConfig(config.wechat_app_id, config.wechat_app_secret)
        api_client = WechatApiClient(api_config)

        # 上传封面
        cover_data = api_client.upload_media(str(cover_result.image_path), "thumb")

        # 构建文章数据
        article = {
            "title": parsed.title,
            "content": html_content,
            "thumb_media_id": cover_data["media_id"],
            "need_open_comment": 0,
            "only_fans_can_comment": 0,
        }

        # 上传草稿
        result = api_client.upload_draft([article])

        click.echo(f"✅ 文章发布成功!")
        click.echo(f"   Media ID: {result['media_id']}")
        click.echo(f"   📝 请在微信公众号后台查看草稿")

    except MpWeixinError as e:
        click.echo(e.user_message())
        sys.exit(1)
    except Exception as e:
        logger.exception(f"[CLI] 未处理的异常")
        click.echo(f"❌ 发生错误: {e}")
        sys.exit(1)


@main.command()
@click.argument("media_id", type=str)
@click.option("--source", type=click.Path(exists=True), help="指定新的源文件，默认使用原文件")
@click.option("--regenerate-cover", is_flag=True, help="重新生成封面")
@click.pass_context
def update(ctx: click.Context, media_id: str, source: str, regenerate_cover: bool):
    """更新已发布的草稿

    更新微信公众号草稿箱中的文章内容。

    示例:

        mp-weixin update s_UokPQPIM8nkGd3QjvYHFFQq8HUuilOgU2rtin6ZBFfkK10hwHDHqhFr1jhzcIf

        mp-weixin update <media_id> --source new-article.md

        mp-weixin update <media_id> --regenerate-cover
    """
    try:
        # 加载配置
        config = AppConfig.from_env(ctx.obj["env"])
        log_level = "DEBUG" if ctx.obj["verbose"] else config.log_level
        setup_logging(log_level, config.log_file)

        logger.info("[CLI] 微信公众号文章更新工具启动")
        logger.info(f"[CLI] Media ID: {media_id}")

        # 确定源文件
        if not source:
            # 如果没有指定，使用 test_article.md 作为默认源
            source = "test_article.md"
            logger.warning(f"[CLI] 未指定源文件，使用默认: {source}")

        file_path = Path(source)

        # 解析文档
        parser = ParserFactory.get_parser(file_path)
        parsed = parser.parse(file_path)

        logger.info(f"[CLI] 文章标题: {parsed.title}")

        # 转换内容
        builder = WechatHTMLBuilder(config.template_name)
        html_content = builder.build(parsed)

        # 生成封面（如果需要）
        if regenerate_cover:
            logger.info("[CLI] 重新生成封面")
            cover_gen = TemplateCoverGenerator(config.theme_color)
            cover_result = cover_gen.generate(parsed.title, "")

            # 上传新封面
            api_config = WechatConfig(config.wechat_app_id, config.wechat_app_secret)
            api_client = WechatApiClient(api_config)
            cover_data = api_client.upload_media(str(cover_result.image_path), "thumb")
            thumb_media_id = cover_data["media_id"]
            logger.info(f"[CLI] 新封面 media_id: {thumb_media_id}")
        else:
            # 获取原草稿的 thumb_media_id
            logger.info("[CLI] 保持原封面")
            api_config = WechatConfig(config.wechat_app_id, config.wechat_app_secret)
            api_client = WechatApiClient(api_config)
            original_draft = api_client.get_draft(media_id)
            thumb_media_id = original_draft.get("thumb_media_id", "")
            logger.info(f"[CLI] 原封面 media_id: {thumb_media_id}")

        # 构建文章数据（按照微信 API 格式）
        # 注意：articles 是对象，不是数组！
        article_data = {
            "article_type": "news",
            "title": parsed.title,
            "author": parsed.metadata.get("author", ""),
            "digest": "",  # 单图文消息的摘要
            "content": html_content,
            "content_source_url": "",  # 原文链接
            "need_open_comment": 0,
            "only_fans_can_comment": 0,
        }

        # 如果有新封面，添加到文章数据
        if thumb_media_id:
            article_data["thumb_media_id"] = thumb_media_id

        # 更新草稿
        api_config = WechatConfig(config.wechat_app_id, config.wechat_app_secret)
        api_client = WechatApiClient(api_config)

        result = api_client.update_draft(media_id, 0, article_data)

        click.echo(f"✅ 草稿更新成功!")
        click.echo(f"   Media ID: {media_id}")
        click.echo(f"   标题: {parsed.title}")
        click.echo(f"   📝 请在微信公众号后台查看更新后的草稿")

    except MpWeixinError as e:
        click.echo(e.user_message())
        sys.exit(1)
    except Exception as e:
        logger.exception(f"[CLI] 未处理的异常")
        click.echo(f"❌ 发生错误: {e}")
        sys.exit(1)


@main.command()
def version():
    """显示版本信息"""
    try:
        from config import __version__
        click.echo(f"mp-weixin-skills version {__version__}")
    except ImportError:
        click.echo("mp-weixin-skills version 0.1.0")


if __name__ == "__main__":
    main()
