from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "مدیریت فروشگاه کامپ‌لند"
admin.site.site_title = "پنل مدیریت"
admin.site.index_title = "محصولات، سفارش‌ها و کاربران"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("accounts/", include("accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
