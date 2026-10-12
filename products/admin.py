from django.contrib import admin

from products.models import Brand, Category, Product, ProductSpec


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 2


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "price", "discount", "stock", "sales")
    list_filter = ("category", "brand")
    search_fields = ("name", "brand__name")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductSpecInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
