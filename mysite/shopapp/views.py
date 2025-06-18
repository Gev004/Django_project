import json
from timeit import default_timer

from django.contrib.syndication.views import Feed
from django.contrib.sitemaps import Sitemap
from django.core.cache import cache
from django.core.serializers import serialize
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.models import Group, User
from django.http import HttpResponse, HttpRequest, HttpResponseForbidden, JsonResponse, Http404
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView,DeleteView,UpdateView,ListView,DetailView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets,filters
from .serializers import ProductSerializer,OrderSerializer
from .forms import ProductForm, OrderForm
from .models import Product, Order
import logging

logger = logging.getLogger(__name__)

class LatestProductsFeed(Feed):
    title = "Latest Products"
    link = "/products/latest/feed/"
    description = "New products added to the shop"

    def items(self):
        return Product.objects.order_by('-id')[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return f"Price: {item.price}"

    def item_link(self, item):
        return item.get_absolute_url()

class ShopSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.5

    def items(self):
        return Product.objects.order_by('-created_at')

    def lastmod(self, obj):
        return obj.created_at


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'created_at']
    ordering_fields = ['created_at']


class Flan(View):
    def get(self, request):
        message = _("Hello, world!")
        return HttpResponse(f"<h1>{message}<h1>")

@cache_page(60)
def shop_index(request: HttpRequest):
    products = [
        ('Laptop', 1999),
        ('Desktop', 2999),
        ('Smartphone', 999),
    ]
    context = {
        "time_running": default_timer(),
        "products": products,
    }
    logger.info("Hello")
    return render(request, 'shopapp/shop-index.html', context=context)


def groups_list(request: HttpRequest):
    context = {
        "groups": Group.objects.prefetch_related('permissions').all(),
    }
    return render(request, 'shopapp/groups-list.html', context=context)


class ProductListView(ListView):
    model = Product()
    template_name = 'shopapp/products-list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter()

class ProductDetailView(DetailView):
    model = Product
    template_name = 'shopapp/product-detail.html'
    context_object_name = 'product'

class CreateProductView(CreateView):
    model = Product
    template_name = 'shopapp/create-product.html'
    form_class = ProductForm
    permission_required = 'shopapp.can_create_product'
    raise_exception = True
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class UpdateProductView(UpdateView):
    model = Product
    template_name = 'shopapp/update-product.html'
    form_class = ProductForm
    success_url = reverse_lazy('shopapp:products_list')
    permission_required = 'shopapp.can_update_product'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if not request.user.has_perm('shopapp.can_update_product'):
            return HttpResponseForbidden("You don't have permission to edit this product.")

        if  obj.created_by != request.user:
            return HttpResponseForbidden("You can only edit products you created.")

        return super().dispatch(request, *args, **kwargs)

class ArchiveProductView(View):
    template_name = 'shopapp/archive-product.html'

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return render(request, self.template_name, {'product': product})

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.archived = True
        product.save()
        return redirect(reverse_lazy('shopapp:products_list'))

class OrderListView(ListView):
    model = Order
    template_name = 'shopapp/orders-list.html'
    context_object_name = 'orders'

class OrderDetailView(PermissionRequiredMixin,DetailView):
    model = Order
    template_name = 'shopapp/order-detail.html'
    context_object_name = 'order'
    permission_required = 'shopapp.view_order'

class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'shopapp/user_orders_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        try:
            self.owner = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404("User not found")

        return Order.objects.filter(user=self.owner).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context


def get_user_orders_json(request, user_id):
    cache_key = f"user_orders_export_json_{user_id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return JsonResponse(cached_data, safe=False)

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404("User not found")

    orders = Order.objects.filter(user=user).order_by('id')

    serialized_data = serialize('json', orders, fields=('delivery_address', 'promocode', 'created_at', 'products'))

    data = json.loads(serialized_data)

    cache.set(cache_key, data, timeout=300)

    return JsonResponse(data, safe=False)

class CreateOrderView(CreateView):
    model = Order
    template_name = 'shopapp/create-order.html'
    form_class = OrderForm
    success_url = reverse_lazy('shopapp:orders_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class UpdateOrderView(UpdateView):
    model = Order
    template_name = 'shopapp/update-order.html'
    form_class = OrderForm
    success_url = reverse_lazy('shopapp:orders_list')


class DeleteOrderView(View):
    template_name = 'shopapp/delete-order.html'

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        return render(request, self.template_name, {'order': order})

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        order.delete()
        return redirect(reverse_lazy('shopapp:orders_list'))

@user_passes_test(lambda u: u.is_staff)
def orders_export_view(request):
    orders = Order.objects.all().prefetch_related('products')
    data = {
        "orders": [
            {
                "id": order.id,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.id,
                "product_ids": list(order.products.values_list('id', flat=True)),
            }
            for order in orders
        ]
    }
    return JsonResponse(data)