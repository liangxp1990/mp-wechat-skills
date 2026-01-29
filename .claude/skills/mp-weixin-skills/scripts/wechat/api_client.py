"""微信公众号 API 客户端"""

import logging
import json
from typing import Dict
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.exceptions import WechatApiError

logger = logging.getLogger(__name__)


@dataclass
class WechatConfig:
    """微信公众号配置"""

    app_id: str
    app_secret: str
    base_url: str = "https://api.weixin.qq.com"
    timeout: int = 30


class WechatApiClient:
    """微信公众号 API 客户端"""

    ENDPOINTS = {
        "token": "/cgi-bin/token",
        "upload_media": "/cgi-bin/material/add_material",
        "upload_draft": "/cgi-bin/draft/add",
        "update_draft": "/cgi-bin/draft/update",
        "get_draft": "/cgi-bin/draft/get",
    }

    def __init__(self, config: WechatConfig):
        logger.info(f"[WechatAPI] 初始化客户端 - AppID: {config.app_id[:8]}***")
        self.config = config
        self._access_token: str = ""
        self._session = self._create_session()

    def _create_session(self) -> requests.Session:
        """创建 HTTP 会话"""
        logger.debug("[WechatAPI] 创建 HTTP 会话")
        session = requests.Session()

        retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)

        return session

    def get_access_token(self) -> str:
        """获取访问令牌"""
        if self._access_token:
            logger.debug("[WechatAPI] 使用缓存的 access_token")
            return self._access_token

        logger.info("[WechatAPI] 请求新的 access_token")
        url = f"{self.config.base_url}{self.ENDPOINTS['token']}"
        params = {
            "grant_type": "client_credential",
            "appid": self.config.app_id,
            "secret": self.config.app_secret,
        }

        try:
            response = self._session.get(url, params=params, timeout=self.config.timeout)
            response.raise_for_status()

            data = response.json()

            if "access_token" not in data:
                error_msg = f"获取 access_token 失败: {data.get('errmsg', '未知错误')}"
                logger.error(f"[WechatAPI] {error_msg}")
                raise WechatApiError(error_msg, data.get("errcode"))

            self._access_token = data["access_token"]
            logger.info(f"[WechatAPI] access_token 获取成功")
            return self._access_token

        except requests.RequestException as e:
            logger.error(f"[WechatAPI] 网络请求失败: {e}")
            raise WechatApiError(f"网络请求失败: {e}")

    def upload_media(self, file_path: str, media_type: str = "thumb") -> Dict:
        """上传永久素材"""
        logger.info(f"[WechatAPI] 开始上传素材 - 类型: {media_type}")

        url = f"{self.config.base_url}{self.ENDPOINTS['upload_media']}"
        params = {
            "access_token": self.get_access_token(),
            "type": media_type,
        }

        try:
            with open(file_path, "rb") as f:
                files = {"media": f}
                response = self._session.post(url, params=params, files=files, timeout=self.config.timeout)

            response.raise_for_status()
            data = response.json()

            if "media_id" not in data:
                error_msg = f"上传素材失败: {data.get('errmsg', '未知错误')}"
                logger.error(f"[WechatAPI] {error_msg}")
                raise WechatApiError(error_msg, data.get("errcode"))

            logger.info(f"[WechatAPI] 素材上传成功")
            return data

        except (requests.RequestException, IOError) as e:
            logger.error(f"[WechatAPI] 上传失败: {e}")
            raise WechatApiError(f"上传失败: {e}")

    def upload_draft(self, articles: list) -> Dict:
        """上传草稿"""
        logger.info(f"[WechatAPI] 开始上传草稿")

        url = f"{self.config.base_url}{self.ENDPOINTS['upload_draft']}"
        params = {"access_token": self.get_access_token()}
        payload = {"articles": articles}

        logger.debug(f"[WechatAPI] 草稿数据: {payload}")

        # 手动序列化 JSON，确保中文不被转义
        data = json.dumps(payload, ensure_ascii=False)

        try:
            headers = {"Content-Type": "application/json; charset=utf-8"}
            response = self._session.post(url, params=params, data=data.encode("utf-8"), headers=headers, timeout=self.config.timeout)

            logger.debug(f"[WechatAPI] 响应状态码: {response.status_code}")
            response.raise_for_status()

            data = response.json()
            logger.debug(f"[WechatAPI] 响应数据: {data}")

            # 检查是否有错误码（有 errcode 且不等于 0 表示有错误）
            errcode = data.get("errcode")
            if errcode is not None and errcode != 0:
                error_msg = f"上传草稿失败: {data.get('errmsg', '未知错误')}"
                logger.error(f"[WechatAPI] {error_msg}")
                raise WechatApiError(error_msg, errcode)

            # 成功响应包含 media_id
            media_id = data.get("media_id")
            if media_id:
                logger.info(f"[WechatAPI] 草稿上传成功 - media_id: {media_id}")
            else:
                logger.info(f"[WechatAPI] 草稿上传成功")
            return data

        except requests.RequestException as e:
            logger.error(f"[WechatAPI] 草稿上传失败: {e}")
            raise WechatApiError(f"草稿上传失败: {e}")

    def get_draft(self, media_id: str) -> Dict:
        """获取草稿详情"""
        logger.info(f"[WechatAPI] 开始获取草稿详情 - media_id: {media_id}")

        url = f"{self.config.base_url}{self.ENDPOINTS['get_draft']}"
        params = {"access_token": self.get_access_token()}
        payload = {"media_id": media_id}

        # 手动序列化 JSON，确保中文不被转义
        data = json.dumps(payload, ensure_ascii=False)

        try:
            headers = {"Content-Type": "application/json; charset=utf-8"}
            response = self._session.post(url, params=params, data=data.encode("utf-8"), headers=headers, timeout=self.config.timeout)
            response.raise_for_status()

            result = response.json()
            logger.debug(f"[WechatAPI] 响应数据: {result}")

            # 检查是否有错误码
            errcode = result.get("errcode")
            if errcode is not None and errcode != 0:
                error_msg = f"获取草稿失败: {result.get('errmsg', '未知错误')}"
                logger.error(f"[WechatAPI] {error_msg}")
                raise WechatApiError(error_msg, errcode)

            # 从返回的数据中提取文章信息
            # 返回格式: {"news_item": [{...文章数据...}]}
            articles = result.get("news_item", [])
            if articles:
                logger.info(f"[WechatAPI] 草稿获取成功 - 文章数: {len(articles)}")
                return articles[0]  # 返回第一篇文章的数据
            else:
                logger.warning(f"[WechatAPI] 草稿中没有文章")
                return {}

        except requests.RequestException as e:
            logger.error(f"[WechatAPI] 获取草稿失败: {e}")
            raise WechatApiError(f"获取草稿失败: {e}")

    def update_draft(self, media_id: str, index: int, article: Dict) -> Dict:
        """更新草稿"""
        logger.info(f"[WechatAPI] 开始更新草稿 - media_id: {media_id}")

        url = f"{self.config.base_url}{self.ENDPOINTS['update_draft']}"
        params = {"access_token": self.get_access_token()}

        # 注意：articles 是对象，不是数组；index 需要转换为字符串
        payload = {"media_id": media_id, "index": str(index), "articles": article}

        # 手动序列化 JSON，确保中文不被转义
        data = json.dumps(payload, ensure_ascii=False)
        logger.info(f"[WechatAPI] 请求体: {data}")

        try:
            headers = {"Content-Type": "application/json; charset=utf-8"}
            response = self._session.post(url, params=params, data=data.encode("utf-8"), headers=headers, timeout=self.config.timeout)
            response.raise_for_status()

            data = response.json()
            logger.debug(f"[WechatAPI] 响应数据: {data}")

            # 检查是否有错误码
            errcode = data.get("errcode")
            if errcode is not None and errcode != 0:
                error_msg = f"更新草稿失败: {data.get('errmsg', '未知错误')}"
                logger.error(f"[WechatAPI] {error_msg}")
                raise WechatApiError(error_msg, errcode)

            logger.info(f"[WechatAPI] 草稿更新成功")
            return data

        except requests.RequestException as e:
            logger.error(f"[WechatAPI] 更新失败: {e}")
            raise WechatApiError(f"更新失败: {e}")
