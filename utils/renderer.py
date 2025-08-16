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
        response_status = renderer_context.get("response").status_code
        request = renderer_context.get("request")
        trace_id = getattr(request, "trace_id", None)

        # 如果已经是 CustomResponse 格式，就直接渲染
        if isinstance(data, dict) and "code" in data and "msg" in data:
            if trace_id and "trace_id" not in data:
                data["trace_id"] = trace_id
            return super().render(data, accepted_media_type, renderer_context)

        # 否则是异常响应，构造统一结构
        response = {
            "code": response_status,
            "msg": data.get("detail", "error") if isinstance(data, dict) else "error",
            "data": None,
        }
        if isinstance(data, dict) and "detail" not in data:
            response["errors"] = data
        if trace_id:
            response["trace_id"] = trace_id

        return super().render(response, accepted_media_type, renderer_context)
