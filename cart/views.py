from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cart.cart import get_cart, next_url, save_qty
from products.models import Product


def cart_detail(request):
    return render(request, "cart.html", get_cart(request))


@require_POST
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    if product.in_stock:
        qty = int(request.POST.get("qty", 1) or 1)
        save_qty(request, product, request.session.get("cart", {}).get(str(product.id), 0) + qty)
        messages.success(request, f"«{product.name}» به سبد خرید اضافه شد.")
    else:
        messages.error(request, "این کالا فعلاً ناموجود است.")
    return redirect(next_url(request))


@require_POST
def update_cart(request, id):
    product = get_object_or_404(Product, id=id)
    save_qty(request, product, int(request.POST.get("qty", 1) or 0))
    return redirect(next_url(request))
