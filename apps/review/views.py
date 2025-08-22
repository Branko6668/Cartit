"""
Review 模块视图

- 提供评论的增删改查接口以及按用户/商品/店铺的查询
- 所有响应统一使用 CustomResponse 封装
- destroy 为软删除（仅置位 is_deleted）
- 列表接口支持分页（使用 DRF 默认分页器配置）
"""
from typing import Any
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from .models import ProductReview
from .serializers import ProductReviewSerializer
from utils.renderer import CustomResponse
from utils.error_codes import Codes


class ProductReviewViewSet(ModelViewSet):
    """商品评论视图集。

    标准动作：list/retrieve/create/update/partial_update/destroy
    自定义动作：by_user/by_product/by_store（均支持分页）
    """

    queryset = ProductReview.objects.filter(is_deleted=False)
    serializer_class = ProductReviewSerializer

    # 标准动作统一包装响应
    def list(self, request, *args: Any, **kwargs: Any):
        """获取评论列表，遵循分页配置。"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination = self.get_paginated_response(serializer.data).data
            return CustomResponse(code=Codes.REVIEW_LIST_OK, data=pagination)
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(code=Codes.REVIEW_LIST_OK, data=serializer.data)

    def retrieve(self, request, *args: Any, **kwargs: Any):
        """获取单条评论详情。"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse(code=Codes.REVIEW_LIST_OK, data=serializer.data)

    def create(self, request, *args: Any, **kwargs: Any):
        """创建评论。"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return CustomResponse(code=Codes.REVIEW_CREATED, data=serializer.data, status=201, headers=headers)

    def update(self, request, *args: Any, **kwargs: Any):
        """更新评论（全量/部分）。"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return CustomResponse(code=Codes.REVIEW_UPDATED, data=serializer.data)

    def partial_update(self, request, *args: Any, **kwargs: Any):
        """部分更新评论。"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args: Any, **kwargs: Any):
        """软删除评论（置 is_deleted=True）。"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return CustomResponse(code=Codes.REVIEW_DELETED, msg="deleted")

    def perform_destroy(self, instance: ProductReview) -> None:
        """软删除实现：仅更新 is_deleted 字段。"""
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])

    # 自定义动作统一包装响应，并支持分页
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id: str = None):
        """按用户查询评论，支持分页。"""
        queryset = self.filter_queryset(self.get_queryset().filter(user_id=user_id))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination = self.get_paginated_response(serializer.data).data
            return CustomResponse(code=Codes.REVIEW_LIST_OK, data=pagination)
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(code=Codes.REVIEW_LIST_OK, data=serializer.data)

    @action(detail=False, methods=['get'], url_path='product/(?P<product_id>[^/.]+)')
    def by_product(self, request, product_id: str = None):
        """按商品查询评论，支持分页。"""
        queryset = self.filter_queryset(self.get_queryset().filter(product_id=product_id))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination = self.get_paginated_response(serializer.data).data
            return CustomResponse(code=Codes.REVIEW_LIST_OK, data=pagination)
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(code=Codes.REVIEW_LIST_OK, data=serializer.data)

    @action(detail=False, methods=['get'], url_path='store/(?P<store_id>[^/.]+)')
    def by_store(self, request, store_id: str = None):
        """按店铺查询评论，支持分页。"""
        queryset = self.filter_queryset(self.get_queryset().filter(store_id=store_id))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination = self.get_paginated_response(serializer.data).data
            return CustomResponse(code=Codes.REVIEW_LIST_OK, data=pagination)
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(code=Codes.REVIEW_LIST_OK, data=serializer.data)
