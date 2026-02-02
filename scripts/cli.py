"""命令行接口（简化版）- 仅保留图片上传功能

注意：文章发布功能由 AI 直接完成（使用 publish.py），此脚本仅用于素材管理。
"""

import sys
import logging
from pathlib import Path
import click

from config import AppConfig
from utils.logger import setup_logging
from wechat.api_client import WechatApiClient, WechatConfig
from exceptions import MpWeixinError

logger = logging.getLogger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--env", default=".env", help="Environment file path")
@click.pass_context
def main(ctx: click.Context, verbose: bool, env: str):
    """微信公众号素材管理工具

    用于上传和管理微信公众号素材库中的图片。
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["env"] = env


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--type", "media_type", default="image", type=click.Choice(["thumb", "image"], case_sensitive=False), help="素材类型")
@click.pass_context
def upload_image(ctx: click.Context, file: str, media_type: str):
    """上传单张图片到微信素材库

    示例:

        mp-weixin upload-image cover.jpg                 # 上传为图片

        mp-weixin upload-image cover.jpg --type thumb    # 上传为缩略图
    """
    try:
        # 加载配置
        config = AppConfig.from_env(ctx.obj["env"])
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
@click.pass_context
def upload_images(ctx: click.Context, directory: str, media_type: str, pattern: str):
    """批量上传文件夹中的图片到微信素材库

    示例:

        mp-weixin upload-images ./images                    # 上传 images 文件夹中的所有 JPG 图片

        mp-weixin upload-images ./photos --pattern "*.png" # 上传所有 PNG 图片

        mp-weixin upload-images ./covers --type thumb      # 上传为缩略图
    """
    try:
        # 加载配置
        config = AppConfig.from_env(ctx.obj["env"])
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


if __name__ == "__main__":
    main()
