# renderer.py

from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

class CustomResponse(Response):
    def __init__(self, code=0, msg="success", data=None, status=200, action=None, errors=None, sub_code=None, **kwargs):
        content = {
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
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response")
        request = renderer_context.get("request")
        status_code = response.status_code
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