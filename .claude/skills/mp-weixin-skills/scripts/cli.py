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
from covers.image_search_maker import ImageSearchCoverGenerator
from covers.browser_search_maker import BrowserSearchCoverGenerator
from wechat import WechatApiClient, WechatConfig
from exceptions import MpWeixinError

logger = logging.getLogger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--env", default=".env", help="Environment file path")
@click.pass_context
def main(ctx: click.Context, verbose: bool, env: str):
    """微信公众号文章发布工具

    一个强大的工具，将 Markdown 文档转换为符合微信公众号排版要求的格式。
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["env"] = env


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--no-api", is_flag=True, help="不使用 API，仅生成 HTML 文件")
@click.option("--template", default="default", help="Style template name")
@click.option("--cover-type", default="browser", type=click.Choice(["browser", "search", "template"], case_sensitive=False), help="Cover generation type: browser (Pexels), search (Unsplash), template")
@click.pass_context
def publish(ctx: click.Context, file: str, no_api: bool, template: str, cover_type: str):
    """发布文章到微信公众号

    将 Markdown 文件转换为微信公众号格式，并可选上传到草稿箱。

    示例:

        mp-weixin publish article.md                    # 使用 API 上传

        mp-weixin publish article.md --no-api          # 仅生成 HTML 文件

        mp-weixin publish article.md --template fancy  # 使用指定模板
    """
    try:
        # 加载配置
        config = AppConfig.from_env(ctx.obj["env"])
        log_level = "DEBUG" if ctx.obj["verbose"] else config.log_level
        setup_logging(log_level, config.log_file)

        logger.info("[CLI] 微信公众号文章发布工具启动")

        # 解析文档
        file_path = Path(file)
        parser = ParserFactory.get_parser(file_path)
        parsed = parser.parse(file_path)

        logger.info(f"[CLI] 文章标题: {parsed.title}")

        # 转换内容
        builder = WechatHTMLBuilder(template)
        html_content = builder.build(parsed)

        # 生成封面
        if cover_type == "template":
            cover_gen = TemplateCoverGenerator(config.theme_color)
        elif cover_type == "browser":
            # 浏览器搜索（默认，使用 Pexels）
            cover_gen = BrowserSearchCoverGenerator(config.theme_color)
        else:  # search (Unsplash)
            from covers.image_search_maker import ImageSearchCoverGenerator
            cover_gen = ImageSearchCoverGenerator(config.theme_color)

        cover_result = cover_gen.generate(parsed.title, "")

        if no_api or not config.has_wechat_api():
            # 手动模式
            logger.info("[CLI] 运行在手动模式")

            output_dir = config.output_dir
            output_dir.mkdir(parents=True, exist_ok=True)

            # 保存 HTML
            html_file = output_dir / f"{file_path.stem}.html"
            html_file.write_text(html_content, encoding="utf-8")

            click.echo(f"✅ 转换完成!")
            click.echo(f"   HTML: {html_file}")
            click.echo(f"   封面: {cover_result.image_path}")
            click.echo(f"\n📝 请手动上传到微信公众号后台")

        else:
            # API 模式
            logger.info("[CLI] 运行在 API 模式")

            api_config = WechatConfig(config.wechat_app_id, config.wechat_app_secret)
            api_client = WechatApiClient(api_config)

            # 处理文章中的图片：提取、上传到微信素材库、替换链接
            from utils.image_extractor import ImageExtractor
            from utils.image_processor import ImageProcessor

            logger.info("[CLI] 开始处理文章中的图片")

            # 提取并处理图片
            extractor = ImageExtractor(config.temp_dir)
            image_processor = ImageProcessor(api_client, config.temp_dir)

            # 从原始 Markdown 中提取图片信息（如果有）
            markdown_content = file_path.read_text(encoding='utf-8')
            images, local_images = extractor.extract_and_prepare_images(
                markdown_content, 'markdown', file_path.parent
            )

            if images:
                logger.info(f"[CLI] 发现 {len(images)} 张图片，正在上传到微信素材库")

                # 处理图片并替换 HTML 中的链接
                html_content = image_processor.process_images(html_content, images, "image")

                # 显示上传结果
                success_count = sum(1 for img in images if 'wechat_url' in img or img.get('uploaded'))
                click.echo(f"   图片上传: {success_count}/{len(images)} 张成功")
            else:
                logger.info("[CLI] 文章中没有发现图片")

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
            logger.info("[CLI] 重新生成封面（使用图片搜索）")
            cover_gen = ImageSearchCoverGenerator(config.theme_color)
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
@click.argument("file", type=click.Path(exists=True))
@click.option("--type", "media_type", default="image", type=click.Choice(["thumb", "image"], case_sensitive=False), help="素材类型")
@click.option("--env", default=".env", help="环境文件路径")
@click.pass_context
def upload_image(ctx: click.Context, file: str, media_type: str, env: str):
    """上传单张图片到微信素材库

    示例:

        mp-weixin upload-image cover.jpg                 # 上传为图片

        mp-weixin upload-image cover.jpg --type thumb    # 上传为缩略图
    """
    try:
        # 加载配置
        config = AppConfig.from_env(env or ctx.obj.get("env", ".env"))
        setup_logging(config.log_level, config.log_file)

        logger.info("[CLI] 微信公众号图片上传工具启动")
        logger.info(f"[CLI] 文件: {file}")
        logger.info(f"[CLI] 类型: {media_type}")

        # 验证 API 配置
        if not config.has_wechat_api():
            click.echo("❌ 未配置微信 API 凭证，请在 .env 文件中设置 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
            sys.exit(1)

        # 初始化 API 客户端
        api_config = WechatConfig(config.wechat_app_id, config.wechat_app_secret)
        api_client = WechatApiClient(api_config)

        # 上传图片
        result = api_client.upload_media(file, media_type)

        click.echo(f"✅ 图片上传成功!")
        click.echo(f"   Media ID: {result['media_id']}")
        click.echo(f"   URL: {result.get('url', '暂无')}")
        click.echo(f"   类型: {media_type}")

    except MpWeixinError as e:
        click.echo(e.user_message())
        sys.exit(1)
    except Exception as e:
        logger.exception(f"[CLI] 未处理的异常")
        click.echo(f"❌ 发生错误: {e}")
        sys.exit(1)


@main.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--type", "media_type", default="image", type=click.Choice(["thumb", "image"], case_sensitive=False), help="素材类型")
@click.option("--pattern", default="*.jpg", help="文件匹配模式")
@click.option("--env", default=".env", help="环境文件路径")
@click.pass_context
def upload_images(ctx: click.Context, directory: str, media_type: str, pattern: str, env: str):
    """批量上传文件夹中的图片到微信素材库

    示例:

        mp-weixin upload-images ./images                    # 上传 images 文件夹中的所有 JPG 图片

        mp-weixin upload-images ./photos --pattern "*.png" # 上传所有 PNG 图片

        mp-weixin upload-images ./covers --type thumb      # 上传为缩略图
    """
    try:
        # 加载配置
        config = AppConfig.from_env(env or ctx.obj.get("env", ".env"))
        setup_logging(config.log_level, config.log_file)

        logger.info("[CLI] 微信公众号批量图片上传工具启动")
        logger.info(f"[CLI] 目录: {directory}")
        logger.info(f"[CLI] 模式: {pattern}")
        logger.info(f"[CLI] 类型: {media_type}")

        # 验证 API 配置
        if not config.has_wechat_api():
            click.echo("❌ 未配置微信 API 凭证，请在 .env 文件中设置 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
            sys.exit(1)

        # 初始化 API 客户端
        api_config = WechatConfig(config.wechat_app_id, config.wechat_app_secret)
        api_client = WechatApiClient(api_config)

        # 查找图片文件
        dir_path = Path(directory)
        image_files = list(dir_path.glob(pattern))

        if not image_files:
            click.echo(f"⚠️  未找到匹配的图片文件: {pattern}")
            sys.exit(0)

        click.echo(f"📁 找到 {len(image_files)} 个图片文件\n")

        # 批量上传
        results = []
        success_count = 0
        fail_count = 0

        for i, image_file in enumerate(image_files, 1):
            click.echo(f"[{i}/{len(image_files)}] 上传: {image_file.name}...", nl=False)
            try:
                result = api_client.upload_media(str(image_file), media_type)
                results.append({"file": image_file.name, "media_id": result["media_id"], "status": "success"})
                success_count += 1
                click.echo(" ✅")
            except Exception as e:
                results.append({"file": image_file.name, "error": str(e), "status": "failed"})
                fail_count += 1
                click.echo(f" ❌ ({e})")

        # 显示汇总
        click.echo(f"\n{'='*60}")
        click.echo(f"✅ 上传完成!")
        click.echo(f"   成功: {success_count}")
        click.echo(f"   失败: {fail_count}")
        click.echo(f"{'='*60}\n")

        # 显示成功的上传结果
        if success_count > 0:
            click.echo("📋 成功上传的图片:")
            click.echo(f"{'文件名':<30} {'Media ID':<30}")
            click.echo("-" * 60)
            for r in results:
                if r["status"] == "success":
                    click.echo(f"{r['file']:<30} {r['media_id']:<30}")

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
    from src import __version__
    click.echo(f"mp-weixin-skills version {__version__}")


if __name__ == "__main__":
    main()
