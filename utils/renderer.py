from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_status = renderer_context.get("response").status_code
        request = renderer_context.get("request")
        trace_id = getattr(request, "trace_id", None)

        response = {
            "code": 0,
            "msg": "success",
            "data": data,
        }

        if trace_id:
            response["trace_id"] = trace_id

        if not (200 <= response_status < 300):
            response["code"] = response_status
            if isinstance(data, dict):
                response["msg"] = data.get("detail", "error")
                response["errors"] = data if "detail" not in data else None
            else:
                response["msg"] = "error"
            response["data"] = None

        return super().render(response, accepted_media_type, renderer_context)
