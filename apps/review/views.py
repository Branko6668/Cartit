from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from .models import ProductReview
from .serializers import ProductReviewSerializer
from utils.renderer import CustomResponse

class ProductReviewViewSet(ModelViewSet):
    queryset = ProductReview.objects.filter(is_deleted=False)
    serializer_class = ProductReviewSerializer

    # 标准动作统一包装响应
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination = self.get_paginated_response(serializer.data).data
            return CustomResponse(data=pagination)
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return CustomResponse(data=serializer.data, status=201, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return CustomResponse(data=serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return CustomResponse(msg="deleted")

    def perform_destroy(self, instance):
        # 软删除
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])

    # 自定义动作统一包装响应，并支持分页
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        queryset = self.filter_queryset(self.get_queryset().filter(user_id=user_id))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination = self.get_paginated_response(serializer.data).data
            return CustomResponse(data=pagination)
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(data=serializer.data)

    @action(detail=False, methods=['get'], url_path='product/(?P<product_id>[^/.]+)')
    def by_product(self, request, product_id=None):
        queryset = self.filter_queryset(self.get_queryset().filter(product_id=product_id))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination = self.get_paginated_response(serializer.data).data
            return CustomResponse(data=pagination)
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(data=serializer.data)

    @action(detail=False, methods=['get'], url_path='store/(?P<store_id>[^/.]+)')
    def by_store(self, request, store_id=None):
        queryset = self.filter_queryset(self.get_queryset().filter(store_id=store_id))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination = self.get_paginated_response(serializer.data).data
            return CustomResponse(data=pagination)
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(data=serializer.data)
