from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from products.filters import brand_filters, filter_products, spec_filters
from products.models import Brand, Category, Product


def home(request):
    products = Product.objects.select_related("brand")
    return render(request, "home.html", {
        "brands": Brand.objects.all(),
        "bestsellers": products.filter(stock__gt=0).order_by("-sales")[:8],
        "newest": products.order_by("-created_at")[:8],
        "discounts": products.filter(discount__gt=0, stock__gt=0).order_by("-discount")[:8],
    })


def product_list(request, slug=None):
    category = get_object_or_404(Category, slug=slug) if slug else None
    q = request.GET.get("q", "").strip()
    products = filter_products(request, category, q)
    page = Paginator(products, 12).get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)
    title = category.name if category else ("نتایج جستجو" if q else "همه محصولات")

    return render(request, "product_list.html", {
        "category": category,
        "q": q,
        "title": title,
        "page": page,
        "qs": params.urlencode(),
        "brands": brand_filters(category, request),
        "spec_filters": spec_filters(category, request),
        "sort": request.GET.get("sort", "newest"),
    })


def product_api(request):
    category = Category.objects.filter(slug=request.GET.get("category")).first()
    q = request.GET.get("q", "").strip()
    page = Paginator(filter_products(request, category, q), 12).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    html = render_to_string("partials/product_grid.html", {"page": page, "qs": params.urlencode()}, request)
    return JsonResponse({"html": html, "count": page.paginator.count})


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category", "brand").prefetch_related("specs"), slug=slug)
    similar = Product.objects.filter(category=product.category).exclude(id=product.id).select_related("brand")[:4]
    return render(request, "product_detail.html", {
        "product": product,
        "similar": similar,
        "in_compare": product.id in request.session.get("compare", []),
    })


def compare_list(request):
    ids = request.session.get("compare", [])
    products = list(Product.objects.filter(id__in=ids).prefetch_related("specs"))
    products.sort(key=lambda p: ids.index(p.id))

    keys = []
    for product in products:
        for spec in product.specs.all():
            if spec.key not in keys:
                keys.append(spec.key)

    rows = []
    for key in keys:
        values = [next((s.value for s in p.specs.all() if s.key == key), "—") for p in products]
        rows.append((key, values, len(set(values)) > 1))

    return render(request, "compare.html", {"products": products, "rows": rows})


@require_POST
def toggle_compare(request, id):
    product = get_object_or_404(Product, id=id)
    ids = request.session.get("compare", [])
    next_url = request.POST.get("next") or "/compare/"

    if product.id in ids:
        ids.remove(product.id)
        messages.success(request, f"«{product.name}» از مقایسه حذف شد.")
    else:
        first = Product.objects.filter(id__in=ids).first()
        if first and first.category_id != product.category_id:
            messages.error(request, "فقط کالاهای هم‌دسته قابل مقایسه هستند.")
        elif len(ids) >= 4:
            messages.error(request, "حداکثر ۴ کالا را می‌توانید مقایسه کنید.")
        else:
            ids.append(product.id)
            messages.success(request, f"«{product.name}» به مقایسه اضافه شد.")

    request.session["compare"] = ids
    return redirect(next_url)
