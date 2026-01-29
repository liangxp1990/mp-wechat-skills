"""自定义异常类"""

from typing import Dict, Any


class MpWeixinError(Exception):
    """基础异常类"""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def user_message(self) -> str:
        """返回用户友好的错误信息"""
        return self.message


class ParserError(MpWeixinError):
    """文档解析异常"""
    pass


class UnsupportedFileTypeError(ParserError):
    """不支持的文件类型"""

    def __init__(self, file_path: str, file_type: str):
        super().__init__(
            f"不支持的文件类型: {file_type}",
            {"file_path": file_path, "file_type": file_type},
        )

    def user_message(self) -> str:
        return (
            f"❌ 文件格式不支持\n\n"
            f"支持的格式: Markdown (.md), Word (.docx), PDF (.pdf)\n"
            f"请检查文件后缀名是否正确。"
        )


class FileReadError(ParserError):
    """文件读取异常"""

    def __init__(self, file_path: str, reason: str):
        super().__init__(f"文件读取失败: {file_path}", {"file_path": file_path, "reason": reason})

    def user_message(self) -> str:
        return (
            f"❌ 无法读取文件\n\n"
            f"文件: {self.details['file_path']}\n"
            f"原因: {self.details['reason']}\n\n"
            f"请检查：\n"
            f"1. 文件是否存在\n"
            f"2. 是否有读取权限\n"
            f"3. 文件是否损坏"
        )


class WechatApiError(MpWeixinError):
    """微信公众号 API 异常"""

    ERROR_CODES = {
        40001: "AppSecret 错误",
        40013: "不合法的 AppID",
        42001: "access_token 超时",
        45011: "API 调用太频繁",
    }

    def __init__(self, message: str, errcode: int = None):
        super().__init__(message, {"errcode": errcode, "errmsg": message})
        self.errcode = errcode

    def user_message(self) -> str:
        if self.errcode:
            friendly_msg = self.ERROR_CODES.get(self.errcode, "未知错误")
            return f"❌ 微信公众号 API 错误\n\n错误码: {self.errcode}\n错误信息: {friendly_msg}"
        return f"❌ 微信公众号 API 错误\n\n{self.message}"


class ConversionError(MpWeixinError):
    """内容转换异常"""
    pass
