import csv
import io
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import path

from .forms import CSVImportForm
from .models import Product, Order
from .admin_mixins import ExportAsCSVMixin


class OrderInline(admin.TabularInline):
    model = Product.orders.through


@admin.action(description="Archive products")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",
    ]
    inlines = [
        OrderInline,
    ]
    list_display = "pk", "name", "description_short", "price", "discount", "archived"
    list_display_links = "pk", "name"
    ordering = "-name", "pk"
    search_fields = "name", "description"
    fieldsets = [
        (None, {
           "fields": ("name", "description"),
        }),
        ("Price options", {
            "fields": ("price", "discount"),
            "classes": ("wide", "collapse"),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options. Field 'archived' is for soft delete",
        })
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."




class ProductInline(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
    list_display = "delivery_address", "promocode", "created_at", "user_verbose"
    change_list_template = "admin/shopapp/order/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("import-orders/", self.admin_site.admin_view(self.import_csv), name="import-orders"),
        ]
        return new_urls + urls

    def import_csv(self, request: HttpRequest):
        if request.method == "POST":
            form = CSVImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data["csv_file"]
                decoded_file = csv_file.read().decode("utf-8")
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)

                for row in reader:
                    order = Order.objects.create(
                        user_id=row["user_id"],
                        delivery_address=row["delivery_address"],
                        promocode=row.get("promocode", ""),
                    )

                    product_ids = row["product_ids"].split(",")
                    for pid in product_ids:
                        try:
                            product = Product.objects.get(pk=int(pid))
                            order.products.add(product)
                        except Product.DoesNotExist:
                            continue

                self.message_user(request, "Import went successfuly")
                return redirect("admin:shopapp_order_changelist")
        else:
            form = CSVImportForm()

        context = {
            "form": form,
            "title": "Imort orders from CSV",
        }
        return render(request, "admin/csv_form.html", context)

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username
