"""测试微信 API 客户端"""

from wechat.api_client import WechatApiClient, WechatConfig


def test_wechat_config():
    """测试配置"""
    config = WechatConfig(app_id="test_id", app_secret="test_secret")

    assert config.app_id == "test_id"
    assert config.app_secret == "test_secret"


def test_wechat_client_init():
    """测试客户端初始化"""
    config = WechatConfig(app_id="test_id", app_secret="test_secret")
    client = WechatApiClient(config)

    assert client.config == config
    assert client._session is not None
