from django.urls import path
from .views import ProductMainMenuView, ProductSubMenuView, ProductSubSubMenuView, ProductTagAPIView, ProductQueryAPIView, ProductSearchAPIView


urlpatterns = [
    path("main_menu/", ProductMainMenuView.as_view(), name="product_main_menu"),
    path("sub_menu/", ProductSubMenuView.as_view(), name="product_sub_menu"),
    path("sub_sub_menu/", ProductSubSubMenuView.as_view(), name="product_sub_sub_menu"),
    path("tag/<int:product_tag_id>/<int:page>/", ProductTagAPIView.as_view(), name="product_tag"),
    path("query/<int:id>/", ProductQueryAPIView.as_view(), name="product_query"),
    path("search/", ProductSearchAPIView.as_view(), name="product_search"),
]
