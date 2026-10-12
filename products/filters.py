from django.db.models import ExpressionWrapper, F, IntegerField, Q

from products.models import Brand, Product

SPEC_FILTERS = {
    "cpu": ["سوکت", "تعداد هسته"],
    "motherboard": ["سوکت", "نوع رم"],
    "gpu": ["چیپست", "حافظه"],
    "ram": ["نوع", "ظرفیت"],
    "storage": ["نوع", "ظرفیت"],
    "psu": ["توان", "گواهی بازدهی"],
    "case": ["نوع", "پنل جانبی"],
    "cooler": ["نوع", "سوکت سازگار"],
    "monitor": ["اندازه", "نرخ بروزرسانی"],
    "accessories": ["نوع", "اتصال"],
}


def filter_products(request, category=None, q=""):
    final_price = ExpressionWrapper(F("price") - F("price") * F("discount") / 100, output_field=IntegerField())
    products = Product.objects.select_related("category", "brand").annotate(price_after_discount=final_price)

    if category:
        products = products.filter(category=category)
    if q:
        products = products.filter(Q(name__icontains=q) | Q(brand__name__icontains=q))
    if request.GET.getlist("brand"):
        products = products.filter(brand__slug__in=request.GET.getlist("brand"))
    if request.GET.get("min"):
        products = products.filter(price_after_discount__gte=request.GET["min"])
    if request.GET.get("max"):
        products = products.filter(price_after_discount__lte=request.GET["max"])
    if request.GET.get("stock"):
        products = products.filter(stock__gt=0)

    allowed_keys = SPEC_FILTERS.get(category.slug, []) if category else []
    for key in allowed_keys:
        values = request.GET.getlist(key)
        if values:
            products = products.filter(specs__key=key, specs__value__in=values)

    orders = {"cheap": "price_after_discount", "expensive": "-price_after_discount", "popular": "-sales"}
    return products.distinct().order_by(orders.get(request.GET.get("sort"), "-created_at"))


def brand_filters(category, request):
    brands = Brand.objects.all()
    if category:
        brands = brands.filter(products__category=category)
    checked = request.GET.getlist("brand")
    return [(b.slug, b.name, b.slug in checked) for b in brands.distinct().order_by("name")]


def spec_filters(category, request):
    if not category:
        return {}
    rows = category.products.values_list("specs__key", "specs__value").order_by().distinct()
    options = {}
    for key, value in rows:
        if value and key in SPEC_FILTERS.get(category.slug, []):
            options.setdefault(key, []).append(value)

    result = {}
    for key in SPEC_FILTERS.get(category.slug, []):
        if key in options:
            checked = request.GET.getlist(key)
            result[key] = [(value, value in checked) for value in sorted(options[key])]
    return result
