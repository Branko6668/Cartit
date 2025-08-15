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
        data = {
            "status": 1001,
            "message": message
        }
        return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")
    @staticmethod
    def other(message):
        data = {
            "status": 1002,
            "message": message
        }
        return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")


class ProductResponseMessage:

    @staticmethod
    def success(message):
        data = {
            "status": 2000,
            "message": message
        }
        return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

    @staticmethod
    def fail(message):
        data = {
            "status": 2001,
            "message": message
        }
        return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

    @staticmethod
    def other(message):
        data = {
            "status": 2002,
            "message": message
        }
        return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")