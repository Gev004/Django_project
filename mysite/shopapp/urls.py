from django.urls import path,include
from rest_framework.routers import DefaultRouter

from .views import *

app_name = "shopapp"

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('orders', OrderViewSet)

urlpatterns = [
    path("", shop_index, name="index"),
    path("api/", include(router.urls)),
    path("groups/", groups_list, name="groups_list"),
    path("products/", ProductListView.as_view(), name="products_list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="products_detail"),
    path("orders/", OrderListView.as_view(), name="orders_list"),
    path("orders/<int:user_id>/json/", get_user_orders_json, name="order_json"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("users/<int:user_id>/orders/", UserOrdersListView.as_view(), name="user_orders_list"),
    path("products/create/", CreateProductView.as_view(), name="create_product"),
    path("products/<int:pk>/update/", UpdateProductView.as_view(), name="update_product"),
    path("products/<int:pk>/archive/", ArchiveProductView.as_view(), name="archive_product"),
    path("orders/make/",CreateOrderView.as_view(),name="create_order"),
    path("orders/<int:pk>/update/", UpdateOrderView.as_view(), name="update_order"),
    path("orders/<int:pk>/delete/", DeleteOrderView.as_view(), name="delete_order"),
    path('orders/export/', orders_export_view, name='orders_export'),
    path("hello/", Flan.as_view(), name="hello"),
    path('products/latest/feed/', LatestProductsFeed(), name='product_feed'),
]
