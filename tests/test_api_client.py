"""测试微信 API 客户端"""

from src.wechat.api_client import WechatApiClient, WechatConfig


def test_wechat_config():
    """测试配置"""
    config = WechatConfig(app_id="test_id", app_secret="test_secret")

    assert config.app_id == "test_id"
    assert config.app_secret == "test_secret"
    assert config.base_url == "https://api.weixin.qq.com"
    assert config.timeout == 30


def test_wechat_config_custom():
    """测试自定义配置"""
    config = WechatConfig(
        app_id="test_id",
        app_secret="test_secret",
        base_url="https://custom.api.com",
        timeout=60,
    )

    assert config.base_url == "https://custom.api.com"
    assert config.timeout == 60


def test_wechat_client_init():
    """测试客户端初始化"""
    config = WechatConfig(app_id="test_id", app_secret="test_secret")
    client = WechatApiClient(config)

    assert client.config == config
    assert client._session is not None
    assert client._access_token == ""


def test_wechat_client_endpoints():
    """测试 API 端点定义"""
    assert WechatApiClient.ENDPOINTS["token"] == "/cgi-bin/token"
    assert WechatApiClient.ENDPOINTS["upload_media"] == "/cgi-bin/material/add_material"
    assert WechatApiClient.ENDPOINTS["upload_draft"] == "/cgi-bin/draft/add"
    assert WechatApiClient.ENDPOINTS["update_draft"] == "/cgi-bin/draft/update"
