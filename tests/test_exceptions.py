"""测试异常类"""

from src.exceptions import UnsupportedFileTypeError, WechatApiError


def test_unsupported_file_type_error():
    """测试不支持的文件类型异常"""
    error = UnsupportedFileTypeError("test.xyz", ".xyz")

    assert error.message == "不支持的文件类型: .xyz"
    assert error.details["file_path"] == "test.xyz"
    assert error.details["file_type"] == ".xyz"
    assert "文件格式不支持" in error.user_message()


def test_wechat_api_error():
    """测试微信 API 异常"""
    error = WechatApiError("测试错误", errcode=40001)

    assert error.errcode == 40001
    assert "AppSecret 错误" in error.user_message()
