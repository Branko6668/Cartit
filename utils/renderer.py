"""
自定义响应与渲染器

- CustomResponse: 统一接口返回结构，包含 code/msg/data，可选 action/errors/sub_code
- CustomJSONRenderer: 将普通 DRF 数据或异常转换为统一结构，并附加可选 trace_id

使用建议：
- 视图中直接返回 CustomResponse，以保持结构一致
- 对于未使用 CustomResponse 的场景，渲染器会自动封装 2xx/非 2xx 响应
"""

from typing import Any, Dict, Optional
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


class CustomResponse(Response):
    """统一响应体。

    参数:
      - code: 业务状态码（默认 0 代表成功，可自定义）
      - msg: 描述信息（默认 "success"）
      - data: 业务数据（任意类型）
      - status: HTTP 状态码（默认 200）
      - action: 客户端可选指令（如跳转、刷新等）
      - errors: 详细错误（如表单校验错误字典）
      - sub_code: 子错误码（细分错误场景）
    """

    def __init__(self, code=0, msg="success", data=None, status=200, action=None, errors=None, sub_code=None, **kwargs):
        content: Dict[str, Any] = {
            "code": code,
            "msg": msg,
            "data": data,
        }
        if action:
            content["action"] = action
        if errors:
            content["errors"] = errors
        if sub_code:
            content["sub_code"] = sub_code
        super().__init__(content, status=status, **kwargs)


class CustomJSONRenderer(JSONRenderer):
    """将任意 DRF 响应按统一结构输出。

    行为:
      - 已是标准结构（包含 code/msg）: 透传
      - 2xx 响应: 自动包装为 {code: 2xx, msg: "success", data}
      - 非 2xx 响应: 提取 detail 为 msg，其余放入 errors
      - 支持附加 trace_id（从 request.trace_id 获取）
    """

    def render(self, data: Any, accepted_media_type: Optional[str] = None, renderer_context: Optional[Dict[str, Any]] = None):
        response = renderer_context.get("response") if renderer_context else None
        request = renderer_context.get("request") if renderer_context else None
        status_code = getattr(response, "status_code", 200)
        trace_id = getattr(request, "trace_id", None)

        # 如果已经是标准结构，直接渲染
        if isinstance(data, dict) and "code" in data and "msg" in data:
            if trace_id and "trace_id" not in data:
                data["trace_id"] = trace_id
            return super().render(data, accepted_media_type, renderer_context)

        # 如果是 2xx 响应，自动封装为成功结构
        if 200 <= status_code < 300:
            response_data = {
                "code": status_code,
                "msg": "success",
                "data": data,
            }
            if trace_id:
                response_data["trace_id"] = trace_id
            return super().render(response_data, accepted_media_type, renderer_context)

        # 否则是异常响应
        error_msg = "error"
        if isinstance(data, dict) and "detail" in data:
            error_msg = data["detail"]

        response_data = {
            "code": status_code,
            "msg": error_msg,
            "data": None,
        }

        if isinstance(data, dict) and "detail" not in data:
            response_data["errors"] = data

        if trace_id:
            response_data["trace_id"] = trace_id

        return super().render(response_data, accepted_media_type, renderer_context)