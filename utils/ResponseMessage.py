import json

from django.http import HttpResponse


class MenuResponseMessage:

    @staticmethod
    def success(message):
        data = {
            "status": 1000,
            "message": message
        }
        return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

    @staticmethod
    def fail(message):
        return {
            "status": 1001,
            "message": message
        }

    @staticmethod
    def other(message):
        return {
            "status": 1002,
            "message": message
        }