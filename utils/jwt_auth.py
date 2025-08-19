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
    """
    生成 JWT token。
    :param user_id: 用户ID
    :param username: 用户名（可选）
    :param days: 过期天数
    :param extra: 额外载荷（将被合并）
    :return: JWT 字符串
    """
    payload: Dict = {
        "user_id": user_id,
        "username": username or "",
        "exp": datetime.now(UTC) + timedelta(days=days),
    }
    if extra:
        payload.update(extra)

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    校验并解析 JWT。
    :param token: JWT 字符串
    :return: (payload, error) 其中 error 可能为 'Token 已过期' / 'Token 无效' / None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token 已过期"
    except (jwt.DecodeError, jwt.InvalidTokenError):
        return None, "Token 无效"


class JWTHeaderAuthentication(BaseAuthentication):
    """
    从请求头 Token 中提取 JWT 并验证。
    格式要求：Token: <jwt>
    """

    def authenticate(self, request):
        token = request.META.get("HTTP_TOKEN")
        if not token:
            return None

        payload, error = verify_token(token)
        if error:
            raise AuthenticationFailed(error)

        # 可选：返回匿名用户或根据 user_id 查询真实用户
        user = AnonymousUser()
        return (user, payload)  # payload 可通过 request.auth 获取


class JWTQueryParamAuthentication(BaseAuthentication):
    """
    从 URL 查询参数中提取 JWT 并验证。
    格式要求：?token=<jwt>
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