"""
JWT 认证与工具函数

提供两个入口：
- generate_token: 生成签名的 JWT 字符串
- verify_token: 校验并解析 JWT，返回载荷或错误提示

并提供两种认证方式（任选其一，或同时开启）：
- JWTHeaderAuthentication: 从请求头 Token:<jwt> 中读取
- JWTQueryParamAuthentication: 从查询参数 ?token=<jwt> 中读取

注意：
- 默认使用 HS256 与 settings.SECRET_KEY
- 仅返回 AnonymousUser，业务方可按需替换为真实用户查询
"""

from datetime import datetime, timedelta, UTC
from typing import Optional, Tuple, Dict
import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

# 加密算法
ALGORITHM = "HS256"


def generate_token(user_id: int, username: Optional[str] = None, days: int = 7, extra: Optional[Dict] = None) -> str:
    """生成 JWT token。

    参数:
        user_id: 用户ID
        username: 用户名（可选）
        days: 过期天数（从当前时间起）
        extra: 额外载荷（将被合并到 payload 中）

    返回:
        签名后的 JWT 字符串
    """
    payload: Dict = {
        "user_id": user_id,
        "username": username or "",
        "exp": datetime.now(UTC) + timedelta(seconds=days),
    }
    if extra:
        payload.update(extra)

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> Tuple[Optional[Dict], Optional[str]]:
    """校验并解析 JWT。

    参数:
        token: JWT 字符串

    返回:
        (payload, error)
        - payload: 解码后的载荷字典；失败时为 None
        - error: 错误信息，可能为 "Token 已过期" / "Token 无效" / None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token 已过期"
    except (jwt.DecodeError, jwt.InvalidTokenError):
        return None, "Token 无效"


class JWTHeaderAuthentication(BaseAuthentication):
    """从请求头中提取并验证 JWT。

    使用方式:
      - 客户端应在请求头中携带: Token: <jwt>
      - 服务端通过 request.META["HTTP_TOKEN"] 获取

    返回:
      - 验证通过: (AnonymousUser, payload)
      - 无 Token: None（交由下一个认证类处理）
      - 失败: 抛出 AuthenticationFailed
    """

    def authenticate(self, request):
        token = request.META.get("HTTP_TOKEN")
        if not token:
            return None

        payload, error = verify_token(token)
        if error:
            raise AuthenticationFailed(error)

        # 可选：这里返回匿名用户。若需要返回真实用户，可根据 payload["user_id"] 查询。
        user = AnonymousUser()
        return (user, payload)  # payload 可通过 request.auth 获取


class JWTQueryParamAuthentication(BaseAuthentication):
    """从 URL 查询参数中提取并验证 JWT。

    使用方式:
      - 客户端在 URL 追加 ?token=<jwt>

    返回:
      - 验证通过: (AnonymousUser, payload)
      - 无 Token: None（交由下一个认证类处理）
      - 失败: 抛出 AuthenticationFailed
    """

    def authenticate(self, request):
        token = request.query_params.get("token")
        if not token:
            return None

        payload, error = verify_token(token)
        if error:
            raise AuthenticationFailed(error)

        user = AnonymousUser()
        return (user, payload)